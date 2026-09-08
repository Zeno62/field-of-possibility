#!/usr/bin/env python3
"""Publication entry point; layout settings are separate from the source text."""
import build_v5

# Include padding within the cover height so it fits one printable A4 page.
build_v5.PRINT += '''
.pdf-cover { box-sizing: border-box; height: 242mm; padding-top: 36mm; }
.pdf-cover, .pdf-toc { break-inside: avoid; }
'''

if __name__ == '__main__':
    build_v5.main()
