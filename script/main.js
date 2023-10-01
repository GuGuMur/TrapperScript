async function get_data(content) {
    const requestOptions = {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({content: content,})
    };
    await fetch(`https://trapper-script.gudev.online/main`, requestOptions)
        .then((response) => response.json())
        .then((data) => {
            console.log(data);
            if (data["status"] == true) {
                ssi_modal.notify('success', {
                    className: 'in-page-edit',
                    title: "获取更新后的内容成功！",
                    content: "",
                })
                $('.editArea').val(data.text)
                $('#editSummary').val("//Powered by InPageEdit & Trapper Script")
            }
            else {
                if (data["text"] != "") {
                    ssi_modal.notify('error', {
                        className: 'in-page-edit',
                        title: '该页面似乎不需要Trapper的更新？',
                        content: "...",
                    });
                }
            }
        })
        .catch(e => {
            console.error('Error:', e);
            ssi_modal.notify('error', {
                className: 'in-page-edit',
                title: 'Trapper处理出错！',
                content: e,
            });
            return { "status": false, "text": "" }
        })
}
async function trapper_edit() {
    const title = mw.config.get("wgPageName")
    await InPageEdit.quickEdit({
        page: title,
        revision: mw.config.get("wgRevisionId"),
        editSummary: "$section //Powered by trapper & InPageEdit"
    })
    trapper_data = await get_data($('.editArea').val)
}

mw.hook('InPageEdit.toolbox').add(({ $toolbox }) => {
    $toolbox
        .find('.btn-group.group1')
        .append(
            $('<li>', { class: 'btn-tip-group' }).append(
                $('<div>', { class: 'btn-tip', text: "Trapper" }),
                $('<button>', { class: 'ipe-toolbox-btn fa fa-cub ipe-trapper ' }).click(
                    trapper_edit
                )
            )
        )
    mw.util.addCSS(`
                .ipe-trapper {
                    color: #845EC2;
                }
                `)
})