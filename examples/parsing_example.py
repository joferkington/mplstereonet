"""
Basic quadrant, strike/dip, and rake parsing.

`mplstereonet` expects measurements to follow the
"right-hand-rule" (RHR) to indicate dip direction.

If you have a set of measurements that don't necessarily follow the RHR, there
are a number of parsing and standardization functions in `mplstereonet` to
correct for this.
"""
import mplstereonet

print('Parse quadrant azimuth measurements')
for original in ['N30E', 'E30N', 'W10S', 'N 10 W']:
    azi = mplstereonet.parse_quadrant_measurement(original)
    print('"{}" --> {:.1f}'.format(original, azi))

print('\nParse quadrant strike/dip measurements.')
print('Note that the output follows the right-hand-rule.')

def parse_sd(original, seperator):
    strike, dip = mplstereonet.parse_strike_dip(*original.split(seperator))
    print('"{}" --> Strike: {:.1f}, Dip: {:.1f}'.format(original, strike, dip))

parse_sd('215/10', '/')
parse_sd('215/10E', '/')
parse_sd('215/10NW', '/')
parse_sd('N30E/45NW', '/')
parse_sd('E10N\t20 N', '\t')
parse_sd('W30N/46.7 S', '/')

print("\nSimilarly, you can parse rake measurements that don't follow the RHR.")

def split_rake(original, sep1=None, sep2=None):
    components = original.split(sep1)
    if len(components) == 3:
        return components
    strike, rest = components
    dip, rake = rest.split(sep2)
    return strike, dip, rake

def display_rake(original, sep1, sep2=None):
    components = split_rake(original, sep1, sep2)
    strike, dip, rake = mplstereonet.parse_rake(*components)
    template = '"{}" --> Strike: {:.1f}, Dip: {:.1f}, Rake: {:.1f}'
    print(template.format(original, strike, dip, rake))

original = 'N30E/45NW 10NE'
display_rake(original, '/')

original = '210 45\t30N'
display_rake(original, None)

original = 'N30E/45NW raking 10SW'
display_rake(original, '/', 'raking')
