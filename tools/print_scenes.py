import glob
for p in [r'research/pck_dump/scenes/creature_visuals/silent.tscn',
          r'research/pck_dump/scenes/screens/char_select/char_select_bg_silent.tscn',
          r'research/pck_dump/scenes/combat/energy_counters/silent_energy_counter.tscn',
          r'research/pck_dump/scenes/vfx/card_trail_silent.tscn']:
    try:
        d = open(p, 'rb').read()
    except OSError as e:
        print('missing', p, e)
        continue
    t = d.decode('utf-8', errors='replace')
    i = t.find('[gd_')
    print('=====', p, len(d))
    print(t[i:])
    print()
