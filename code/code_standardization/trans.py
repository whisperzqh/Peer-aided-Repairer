from tree_sitter import Language, Parser


C_LANGUAGE = Language('build/my-languages.so', 'c')


def get(s: str):
    parser = Parser()
    parser.set_language(C_LANGUAGE)
    code = s
    tree = parser.parse(bytes(code, "utf8"))
    st = set()
    kword = {"main", "scanf", "printf", "puts", "gets",
             "putchar", "abs", "fabs", "exp", "fabs", "pow",
             "sqrt", "isdigit"}
    mp = dict()
    token = "g"
    cnt = 0

    # traverse the syntax tree and modify variable names
    def rename_variables(node):
        nonlocal code, cnt, mp
        if node.type == 'identifier':
            # modify variable names
            old_name = node.text.decode('utf-8')
            if old_name not in mp.values() and old_name not in kword:
                if old_name in mp.keys():
                    new_name = mp[old_name]
                else:
                    mp[old_name] = token + str(cnt)
                    cnt += 1
                    new_name = mp[old_name]
                # obtain the range of variable name nodes and replace with new text content
                start_byte = node.start_byte
                end_byte = node.end_byte
                code = code[:start_byte] + new_name + code[end_byte:]
                st.add(new_name)
                return True

        # recursive processing of child nodes
        for child in node.children:
            if rename_variables(child):
                return True
        return False

    root_node = tree.root_node
    while rename_variables(root_node):
        tree = parser.parse(bytes(code, "utf-8"))
        root_node = tree.root_node
    return code
