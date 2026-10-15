// ============ memberref 审计（2026-10-15，v0.5.3 引入） ============
// 用途：mod dll 按 0.111 refs 编译、游戏跑 0.107.1——凡是"参数相同但返回类型不同"或"成员直接删除"的
// API，会在运行时抛 MissingMethodException（"编译过、正式版炸"）。试编译（-p:LsCompatTrial）只能抓
// "成员不存在"，抓不到"仅返回类型不同"（如 CardCmd.Exhaust：0.107=Task / 0.111=Task<CardPileAddResult?>）。
// 本工具在 IL 层做最终校验：把 mod dll 里所有指向 sts2 程序集的 memberref（方法/字段，含返回类型）
// 与目标 sts2.dll 的 methoddef/fielddef 逐签名比对；另查 mod 类型基类/接口的 typeref 是否存在。
//
// 用法：
//   dotnet run --project tools\memberref_audit -- <mod.dll> <目标 sts2.dll> [--verbose]
// 退出码：0=全部命中（可发布）；1=有缺失成员（必须修）。
// 发布 SOP：build 产物 dll 先跑本工具对 0.107 游戏 dll（D:\...\data_sts2_windows_x86_64\sts2.dll），
// 再对 0.111 refs（mod\lightsworn\refs\data\sts2.dll）——两端都干净才算过。
using System.Collections.Immutable;
using System.Reflection;
using System.Reflection.Metadata;
using System.Reflection.Metadata.Ecma335;
using System.Reflection.PortableExecutable;

namespace MemberrefAudit;

internal static class Program
{
    private static int Main(string[] args)
    {
        if (args.Length < 2)
        {
            Console.Error.WriteLine("usage: memberref_audit <mod.dll> <target sts2.dll> [--verbose]");
            return 2;
        }
        string modPath = args[0];
        string targetPath = args[1];
        bool verbose = args.Contains("--verbose");

        using var modPe = new PEReader(File.OpenRead(modPath));
        using var targetPe = new PEReader(File.OpenRead(targetPath));
        var mod = modPe.GetMetadataReader();
        var target = targetPe.GetMetadataReader();

        string targetAsmName = target.IsAssembly ? target.GetString(target.GetAssemblyDefinition().Name) : "sts2";
        Console.WriteLine($"mod   : {modPath}");
        Console.WriteLine($"target: {targetPath} (assembly '{targetAsmName}')");

        // ---------- 目标侧索引 ----------
        var targetTypes = new HashSet<string>(StringComparer.Ordinal);
        var targetMethods = new HashSet<string>(StringComparer.Ordinal);
        var targetFields = new HashSet<string>(StringComparer.Ordinal);
        var provider = new CanonProvider(mod, target);

        foreach (var tdh in target.TypeDefinitions)
        {
            var td = target.GetTypeDefinition(tdh);
            string typeName = TypeName(target, td);
            targetTypes.Add(typeName);
            foreach (var mh in td.GetMethods())
            {
                var md = target.GetMethodDefinition(mh);
                string sig = DecodeMethodSig(target, md.Signature, provider);
                targetMethods.Add($"{typeName}::{target.GetString(md.Name)} {sig}");
            }
            foreach (var fh in td.GetFields())
            {
                var fd = target.GetFieldDefinition(fh);
                string sig = DecodeFieldSig(target, fd.Signature, provider);
                targetFields.Add($"{typeName}::{target.GetString(fd.Name)} {sig}");
            }
        }

        // ---------- mod 侧 memberref 审计 ----------
        var missing = new List<string>();
        int auditedMethods = 0, auditedFields = 0, auditedTypes = 0;

        foreach (var mrh in mod.MemberReferences)
        {
            var mr = mod.GetMemberReference(mrh);
            string? ownerType = ResolveParentType(mod, mr.Parent, targetAsmName);
            if (ownerType == null)
                continue; // 非 sts2 的引用（BCL/Godot/RitsuLib/mod 自身）

            string memberName = mod.GetString(mr.Name);
            switch (mr.GetKind())
            {
                case MemberReferenceKind.Method:
                {
                    auditedMethods++;
                    string sig = DecodeMethodSig(mod, mr.Signature, provider);
                    string key = $"{ownerType}::{memberName} {sig}";
                    if (!targetMethods.Contains(key))
                        missing.Add($"[MISSING METHOD] {key}");
                    else if (verbose)
                        Console.WriteLine($"[ok] {key}");
                    break;
                }
                case MemberReferenceKind.Field:
                {
                    auditedFields++;
                    string sig = DecodeFieldSig(mod, mr.Signature, provider);
                    string key = $"{ownerType}::{memberName} {sig}";
                    if (!targetFields.Contains(key))
                        missing.Add($"[MISSING FIELD]  {key}");
                    break;
                }
            }
        }

        // ---------- mod 类型基类/接口 typeref 审计 ----------
        foreach (var tdh in mod.TypeDefinitions)
        {
            var td = mod.GetTypeDefinition(tdh);
            if (td.GetDeclaringType().IsNil) { /* top-level irrelevant */ }
            var extends = td.BaseType;
            CheckTypeRef(mod, extends, targetAsmName, targetTypes, missing, ref auditedTypes);
            foreach (var ih in td.GetInterfaceImplementations())
            {
                var ii = mod.GetInterfaceImplementation(ih);
                CheckTypeRef(mod, ii.Interface, targetAsmName, targetTypes, missing, ref auditedTypes);
            }
        }

        // ---------- 输出 ----------
        Console.WriteLine();
        Console.WriteLine($"audited: methods={auditedMethods} fields={auditedFields} base/iface typerefs={auditedTypes}");
        if (missing.Count == 0)
        {
            Console.WriteLine("AUDIT PASS: mod dll 的全部 sts2 引用在目标程序集中均存在且签名一致。");
            return 0;
        }
        Console.WriteLine($"AUDIT FAIL: {missing.Count} 处引用在目标程序集中不存在或签名不一致：");
        foreach (string m in missing.Distinct().OrderBy(x => x))
            Console.WriteLine("  " + m);
        return 1;
    }

    private static void CheckTypeRef(MetadataReader mod, EntityHandle handle, string targetAsmName,
        HashSet<string> targetTypes, List<string> missing, ref int audited)
    {
        if (handle.IsNil) return;
        string? full = ResolveParentType(mod, handle, targetAsmName);
        if (full == null) return;
        audited++;
        if (!targetTypes.Contains(full))
            missing.Add($"[MISSING TYPE]   {full}");
    }

    /// <summary>把 memberref/extends/interface 的父类型句柄解析为 "ns.Type"（仅当指向目标程序集时），否则 null。</summary>
    private static string? ResolveParentType(MetadataReader reader, EntityHandle handle, string targetAsmName)
    {
        switch (handle.Kind)
        {
            case HandleKind.TypeReference:
            {
                var tr = reader.GetTypeReference((TypeReferenceHandle)handle);
                if (!IsTargetScope(reader, tr.ResolutionScope, targetAsmName)) return null;
                return TypeName(reader, tr);
            }
            case HandleKind.TypeDefinition:
            {
                // 同一程序集内定义的类型（mod 自身类型）——不是目标程序集引用
                return null;
            }
            case HandleKind.TypeSpecification:
            {
                var ts = reader.GetTypeSpecification((TypeSpecificationHandle)handle);
                var provider = ProviderFor(reader);
                string decoded = ts.DecodeSignature(provider, null);
                // 泛型实例的基类型名："MegaCrit....Foo<...>" → 取到 '<' 之前的本名
                int lt = decoded.IndexOf('<');
                string bare = lt >= 0 ? decoded[..lt] : decoded;
                // 只有属于目标程序集命名空间的才审（用已知目标类型集合判断由调用方做）——这里按前缀粗筛
                return bare.StartsWith("MegaCrit.", StringComparison.Ordinal) ? bare : null;
            }
            default:
                return null;
        }
    }

    private static bool IsTargetScope(MetadataReader reader, EntityHandle scope, string targetAsmName)
    {
        if (scope.Kind != HandleKind.AssemblyReference) return false;
        var ar = reader.GetAssemblyReference((AssemblyReferenceHandle)scope);
        return reader.GetString(ar.Name) == targetAsmName;
    }

    private static string TypeName(MetadataReader reader, TypeDefinition td)
    {
        string ns = reader.GetString(td.Namespace);
        string name = reader.GetString(td.Name);
        return ns.Length == 0 ? name : ns + "." + name;
    }

    private static string TypeName(MetadataReader reader, TypeReference tr)
    {
        string ns = reader.GetString(tr.Namespace);
        string name = reader.GetString(tr.Name);
        return ns.Length == 0 ? name : ns + "." + name;
    }

    // ---------- 签名解码：把签名渲染成规范字符串（含返回类型），跨程序集可比 ----------
    // DecodeMethodSignature 返回的首元素即返回类型（后续为参数）——"仅返回类型不同"的场景在此体现。
    private static string DecodeMethodSig(MetadataReader reader, BlobHandle sig, CanonProvider provider)
    {
        var blobReader = reader.GetBlobReader(sig);
        var decoder = new SignatureDecoder<string, object?>(provider, reader, null);
        var s = decoder.DecodeMethodSignature(ref blobReader);
        return s.ReturnType + " (" + string.Join(",", s.ParameterTypes) + ")";
    }

    private static string DecodeFieldSig(MetadataReader reader, BlobHandle sig, CanonProvider provider)
    {
        var blobReader = reader.GetBlobReader(sig);
        var decoder = new SignatureDecoder<string, object?>(provider, reader, null);
        return decoder.DecodeFieldSignature(ref blobReader);
    }

    private static CanonProvider ProviderFor(MetadataReader reader) => new(reader, null);

    /// <summary>
    /// 规范类型字符串：基元=名字；typeref/typedef=ns.name（跨程序集按名对齐）；typerspec=Base&lt;args&gt;；
    /// 数组/指针/byref=后缀/前缀；泛型参数=!n / !!n。跨程序集比较时名字相同即视为同一类型——
    /// 对本场景（mod 引用游戏 sts2 类型）足够，且能精确复现"返回类型不同"的场景。
    /// </summary>
    private sealed class CanonProvider : ISignatureTypeProvider<string, object?>
    {
        private readonly MetadataReader _reader;
        private readonly MetadataReader? _target;

        public CanonProvider(MetadataReader reader, MetadataReader? target)
        {
            _reader = reader;
            _target = target;
        }

        public string GetPrimitiveType(PrimitiveTypeCode typeCode) => typeCode switch
        {
            PrimitiveTypeCode.Boolean => "System.Boolean",
            PrimitiveTypeCode.Byte => "System.Byte",
            PrimitiveTypeCode.SByte => "System.SByte",
            PrimitiveTypeCode.Char => "System.Char",
            PrimitiveTypeCode.Int16 => "System.Int16",
            PrimitiveTypeCode.UInt16 => "System.UInt16",
            PrimitiveTypeCode.Int32 => "System.Int32",
            PrimitiveTypeCode.UInt32 => "System.UInt32",
            PrimitiveTypeCode.Int64 => "System.Int64",
            PrimitiveTypeCode.UInt64 => "System.UInt64",
            PrimitiveTypeCode.Single => "System.Single",
            PrimitiveTypeCode.Double => "System.Double",
            PrimitiveTypeCode.IntPtr => "System.IntPtr",
            PrimitiveTypeCode.UIntPtr => "System.UIntPtr",
            PrimitiveTypeCode.Object => "System.Object",
            PrimitiveTypeCode.String => "System.String",
            PrimitiveTypeCode.Void => "System.Void",
            PrimitiveTypeCode.TypedReference => "System.TypedReference",
            _ => typeCode.ToString()
        };

        public string GetTypeFromDefinition(MetadataReader reader, TypeDefinitionHandle handle, byte rawTypeKind)
            => TypeName(reader, reader.GetTypeDefinition(handle));

        public string GetTypeFromReference(MetadataReader reader, TypeReferenceHandle handle, byte rawTypeKind)
            => TypeName(reader, reader.GetTypeReference(handle));

        public string GetTypeFromSpecification(MetadataReader reader, object? genericContext, TypeSpecificationHandle handle, byte rawTypeKind)
            => reader.GetTypeSpecification(handle).DecodeSignature(this, genericContext);

        public string GetSZArrayType(string elementType) => elementType + "[]";
        public string GetArrayType(string elementType, ArrayShape shape) => elementType + "[" + new string(',', shape.Rank - 1) + "]";
        public string GetByReferenceType(string elementType) => elementType + "&";
        public string GetPointerType(string elementType) => elementType + "*";
        public string GetFunctionPointerType(MethodSignature<string> signature) => "fnptr";
        public string GetGenericInstantiation(string genericType, ImmutableArray<string> typeArguments)
            => genericType + "<" + string.Join(",", typeArguments) + ">";
        public string GetGenericMethodParameter(object? genericContext, int index) => "!!" + index;
        public string GetGenericTypeParameter(object? genericContext, int index) => "!" + index;
        public string GetModifiedType(string modifier, string unmodifiedType, bool isRequired) => unmodifiedType;
        public string GetPinnedType(string elementType) => elementType;
    }
}
