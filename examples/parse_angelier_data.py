"""
This is meant to serve as an example of slightly more complex parsing of
orientation measurements.

Angelier, 1979's seminal paper on paleostress determination includes a table
of slickenslide measurements from normal faults.

However, some of the measurements are rakes, while others are strike/dip and an
azimuth of the slickenslides ("Rake" measurements without a direction letter
are actually azimuthal measurements.).

Furthermore, the measurements do not follow the right-hand-rule for indicating
dip direction of a plane and they indicate rake direction using a directional
letter.

To unify the measurements for plotting, etc, we need to parse all of the
measurements, and convert the azimuth measurements to rakes.
"""
import os
import matplotlib.pyplot as plt
import mplstereonet

def main():
    strike, dip, rake = load()

    # Plot the data.
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='stereonet')
    ax.rake(strike, dip, rake, 'ro')
    plt.show()

def load():
    """Read data from a text file on disk."""
    # Get the data file relative to this file's location...
    datadir = os.path.dirname(__file__)
    filename = os.path.join(datadir, 'angelier_data.txt')

    data = []
    with open(filename, 'r') as infile:
        for line in infile:
            # Skip comments
            if line.startswith('#'):
                continue

            # First column: strike, second: dip, third: rake.
            strike, dip, rake = line.strip().split()

            if rake[-1].isalpha():
                # If there's a directional letter on the rake column, parse it
                # normally.
                strike, dip, rake = mplstereonet.parse_rake(strike, dip, rake)
            else:
                # Otherwise, it's actually an azimuthal measurement of the
                # slickenslide directions, so we need to convert it to a rake.
                strike, dip = mplstereonet.parse_strike_dip(strike, dip)
                azimuth = float(rake)
                rake = mplstereonet.azimuth2rake(strike, dip, azimuth)

            data.append([strike, dip, rake])

    # Separate the columns back out
    strike, dip, rake = zip(*data)
    return strike, dip, rake

if __name__ == '__main__':
    main()
