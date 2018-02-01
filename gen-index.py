"""
Generate an index for a directory of Eagle library files.

I said I needed to organize these better. We're getting there...
"""
import os
import re
import glob
import argparse

import xml.etree.ElementTree as ET


def read_header(readme_file):
    """
    Read the first part of the README.md file -- up to the `Device Index`
    header.
    """
    header_lines = []

    state = 'find_header'
    with open(readme_file, 'r') as fh:
        for line in fh:
            line = line.rstrip()
            header_lines.append(line)

            if line == 'Device Index' and state == 'find_header':
                # The next line is the "line", e.g.:
                # Device Index
                # ------------
                state = 'find_header_markdown'

            elif state == 'find_header_markdown':
                state = 'done'
                break

    if state != 'done':
        raise ValueError('Failed to find header in readme!')

    return '\n'.join(header_lines)


def generate_library_index(library_file):
    # e.g. - foo/bar/greg-IC.lbr. Extract the filename, remove the extension,
    # take everything after the first -
    library_name = os.path.splitext(os.path.basename(library_file))[0].split('-', 1)[1]

    index_lines = ['\n# %s' % library_name]
    dom = ET.parse(library_file).getroot()
    device_sets = dom.findall('./drawing/library/devicesets/deviceset')
    for device_set in device_sets:
        name = device_set.attrib['name']

        desc_elem = device_set.find('./description')
        if desc_elem is not None:
            raw_desc = desc_elem.text

            # Take the first line of the description and remove any "HTML" (No, you
            # cannot parse HTML with regex, but my descriptions are probably
            # consistent enough that this is fine.
            desc = re.sub('</?[^<]+>', '', raw_desc.splitlines()[0])

            index_lines.append('* **%s** - %s' % (name, desc))
        else:
            index_lines.append('* **%s**' % (name,))

    return '\n'.join(index_lines)


def generate_index(readme_file):
    header = read_header(readme_file)
    index_parts = [header]

    library_dir = os.path.dirname(readme_file)

    for library_file in glob.glob(os.path.join(library_dir, '*-*.lbr')):
        index_parts.append(generate_library_index(library_file))

    with open(readme_file, 'w') as fh:
        for part in index_parts:
            fh.write(part)
            fh.write('\n')


def main():
    parser = argparse.ArgumentParser(description='Generate an index of my Eagle library.')
    parser.add_argument('readme_file', help='Path to readme file.')

    args = parser.parse_args()
    generate_index(args.readme_file)


if __name__ == '__main__':
    main()
