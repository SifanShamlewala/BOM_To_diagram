def filter_render_links(links, device_to_enclosure):
    render_links = []

    for link in links:
        src_enc = device_to_enclosure[link["from"]]
        dst_enc = device_to_enclosure[link["to"]]

        if src_enc != dst_enc:
            render_links.append(link)

    return render_links
