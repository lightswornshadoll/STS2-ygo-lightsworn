import glob
for p in glob.glob(r'research/pck_dump/scenes/merchant/characters/silent_merchant.tscn') + glob.glob(r'research/pck_dump/scenes/rest_site/characters/silent_rest_site.tscn'):
    d = open(p, 'rb').read()
    t = d.decode('utf-8', errors='replace')
    i = t.find('[gd_')
    print('=====', p, len(d))
    print(t[i:i+3000])
    print()
