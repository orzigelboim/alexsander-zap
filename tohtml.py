import os

html_template = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">

    <title>Index</title>
</head>
<body>
    <div class="col-md-6" style="margin:20px;">
        <div class="portlet yellow-lemon box">
            <div class="portlet-title">
                <div class="caption">
                    <i class="fa fa-cogs"></i>אלכסנדר
                </div>
            </div>
            <div class="portlet-body">
                <div id="tree_3" class="tree-demo jstree jstree-3 jstree-default" role="tree" aria-activedescendant="j3_1">
                    <ul class="jstree-container-ul jstree-children">
                        {list_items}
                    </ul>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""

def generate_list_items(xml_files):
    list_items = ""
    for xml_file in xml_files:
        name = input(f"Enter display name for {xml_file}: ")
        list_items += f'''<li role="treeitem" id="j3_14" class="jstree-node jstree-leaf jstree-last" aria-selected="false">
                            <i class="jstree-icon jstree-ocl"></i>
                            <a class="jstree-anchor" href="{xml_file}" target="_self">
                                <i class="jstree-icon jstree-themeicon fa fa-folder icon-state-warning icon-lg jstree-themeicon-custom"></i>{name}
                            </a>
                        </li>\n'''
    return list_items

def main():
    # Get all XML files in the current directory
    xml_files = [f for f in os.listdir('.') if f.endswith('.xml')]
    
    # Generate list items for each XML file
    list_items = generate_list_items(xml_files)
    
    # Create the final HTML content
    html_content = html_template.format(list_items=list_items)
    
    # Write the HTML content to index.html (overwrite if it exists)
    with open("index.html", "w", encoding="utf-8") as file:
        file.write(html_content)
    
    print("index.html has been generated successfully.")

if __name__ == "__main__":
    main()
