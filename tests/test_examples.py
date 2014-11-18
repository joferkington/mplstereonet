"""Runs all examples and compares the output to previously generated output."""
from PIL import Image
import numpy as np
import examples

def test_all_examples():
    """Run all python files in the example directory and compare their output
    with the previously saved output."""
    for filename in examples.example_files():
        output_text, figures = examples.run(filename)
        if output_text:
            compare_text(filename, output_text)
        for fig in figures:
            compare_figure(filename, fig)

def compare_figure(example_filename, fig):
    """Compare a figure object with a previously saved image of it.
    "example_filename" is the filename of the python script used."""
    orig_image_filename = examples.image_filename(example_filename, fig)
    orig_image = Image.open(orig_image_filename)
    new_image = examples.make_pil_image(fig)
    if not similar_images(orig_image, new_image):
        print(example_filename)
        orig_image.show()
        new_image.show()
        assert False

def compare_text(example_filename, output_text):
    """Compare output text with a previously saved version.
    "example_filename" is the filename of the python script used."""
    with open(examples.text_filename(example_filename), 'r') as infile:
        saved_text = infile.read()
        assert output_text == saved_text

def similar_images(orig_image, new_image, tol=1.0e-6):
    """Compare two PIL image objects and return a boolean True/False of whether
    they are similar (True) or not (False). "tol" is a unitless float between
    0-1 that does not depend on the size of the images."""
    orig_image = orig_image.convert('RGB')
    new_image = orig_image.convert('RGB')
    orig_data = np.array(orig_image, dtype=np.int16)
    new_data = np.array(new_image, dtype=np.int16)
    changed = new_data - orig_data

    # Ignore any differences of only one 1 (usually due to changes in
    # antialiasing instead of actual changes).
    changed[np.abs(changed) == 1] = 0

    # Calculate RMS of difference
    changed = changed.reshape(-1)
    rms = changed.dot(changed.astype(int))

    # Turn RMS into a unitless 0-1 float that doesn't depend on image size
    rms = np.sqrt(rms / changed.size) / 255.0
    return rms < tol
