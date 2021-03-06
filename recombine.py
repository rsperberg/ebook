#!/usr/bin/python3

import xml.etree.ElementTree as ET
import sys
import argparse

title_page_template = """\
<div id="title_page" xmlns="http://www.w3.org/1999/xhtml">
  <h1><span class="title">%s</span><br/>
  <span style="font-size:medium;">by</span><br/>
  <span class="author">%s</span></h1>
</div>
"""


def process_bsps(r, bsp_dict):
    out = ET.Element(r.tag, r.attrib)
    def recursive_process(e, cur):
        for c, se in enumerate(list(e)):
            if (se.tag == "{http://www.w3.org/1999/xhtml}div" and
                se.attrib.get("class") == "bsp_block"):
                bsps = se.text.strip().split("…")
                if len(bsps) == 2:
                    #generate bsp list
                    bsp_start_i = int(bsps[0][3:]) + 1
                    bsp_end_i = int(bsps[1][3:])
                    del bsps[1]
                    for i in range(bsp_start_i, bsp_end_i + 1):
                        bsps.append("bsp" + str(i))
                for bsp in bsps:
                    cur.append(bsp_dict[bsp])
            else:
                n = ET.SubElement(cur, se.tag, se.attrib)
                n.text = se.text
                n.tail = se.tail
                recursive_process(se, n)
    recursive_process(r, out)
    return out


def parse_command_line():
    #parse arguments
    parser = argparse.ArgumentParser(description="""\
Recombine skeleton and bsps and optionally add title page, creating final xhtml version.
The title page is generated from the title tag and the author meta tag of the skeleton.""")
    parser.add_argument("-s", "--skeleton", default="skeleton.xhtml",
                        help="Name of 'skeleton' input file (default: 'skeleton.xhtml')")
    parser.add_argument("-b", "--bsps", default="bsps.xhtml",
                        help="Name of 'bog standard paragraphs' input file (default: 'bsps.xhtml')")
    parser.add_argument("-o", "--output", default="recombined.xhtml",
                        help="Output file name (default: 'recombined.xhtml')")
    parser.add_argument("--notitle", action="store_true",
                        help="Do not insert title page.")
    return vars(parser.parse_args())


def main():
    ET.register_namespace('', "http://www.w3.org/1999/xhtml")
    args = parse_command_line()
    main_tree = ET.parse(args["skeleton"])
    removeids = main_tree.findall(
        "./{http://www.w3.org/1999/xhtml}head/"
        "{http://www.w3.org/1999/xhtml}link[@href='include/skel_styles.css']")
    removeids += main_tree.findall(
        "./{http://www.w3.org/1999/xhtml}head/{http://www.w3.org/1999/xhtml}script")
    head = main_tree.find("./{http://www.w3.org/1999/xhtml}head")
    for r in removeids:
        head.remove(r)
    if not args.get("notitle"):
        title = head.find("{http://www.w3.org/1999/xhtml}title").text
        author_tag = (head.find("{http://www.w3.org/1999/xhtml}meta[@name='author']") or
                      head.find("{http://www.w3.org/1999/xhtml}meta[@name='author']"))
        author = author_tag.attrib.get("content")
        title_page = ET.XML(title_page_template % (title, author))
        body = main_tree.find("./{http://www.w3.org/1999/xhtml}body")
        body.insert(0, title_page)
    bsp_tree = ET.parse(args["bsps"])
    bsp_dict = {}
    for e in bsp_tree.iter("{http://www.w3.org/1999/xhtml}div"):
        bsp_dict[e.attrib["id"]] = e.find("{http://www.w3.org/1999/xhtml}p")
    out = process_bsps(main_tree.getroot(), bsp_dict)
    ET.ElementTree(out).write(args["output"],
                              encoding="unicode",
                              xml_declaration=True)





if __name__ == "__main__":
    main()
