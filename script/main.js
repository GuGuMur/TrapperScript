async function get_page_text() {
    return new Promise((resolve, reject) => {
        const jsonGet = {
            action: 'parse',
            page: mw.config.get("wgPageName"),
            prop: 'wikitext',
            format: 'json',
        }
        const mwApi = new mw.Api()
        mwApi
            .get(jsonGet)
            .then((data) => {
                resolve(data.parse.wikitext["*"]);
            })
            .catch((error) => {
                reject(error);
            })
    });
}

async function get_data() {
    var pagetext = await get_page_text()
    // console.log(pagetext)
    const requestOptions = {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ pagetext: pagetext })
    };
    try {
        const response = await fetch(`https://trapper-script.gudev.online/main`, requestOptions);
        const data = await response.json();
        console.log(data);
        if (data["status"] == true) {
            ssi_modal.notify('success', {
                className: 'in-page-edit',
                title: "获取更新后的内容成功！",
                content: "",
            });
            $('.editArea').val(data.text);
            $('#editSummary').val("//Powered by InPageEdit & Trapper Script");
        } else {
            if (data["text"] !== "") {
                ssi_modal.notify('error', {
                    className: 'in-page-edit',
                    title: '该页面似乎不需要Trapper的更新？',
                    content: "...",
                });
            }
        }
    } catch (e) {
        console.error('Error:', e);
        ssi_modal.notify('error', {
            className: 'in-page-edit',
            title: 'Trapper处理出错！',
            content: e.toString(),
        });
        return { "status": false, "text": "" };
    }
}

async function trapper_edit() {
    const title = mw.config.get("wgPageName")
    let info;
    info = InPageEdit.quickEdit({
        page: title,
        revision: mw.config.get("wgRevisionId"),
        editSummary: "$section //Powered by trapper & InPageEdit"
    });
    try {
        const trapper_data = await get_data();
        // 处理 trapper_data 返回值
    } catch (error) {
        console.error('Error:', error);
        // 处理异常情况
    }
}

mw.hook('InPageEdit.toolbox').add(({ $toolbox }) => {
    $toolbox
        .find('.btn-group.group1')
        .append(
            $('<li>', { class: 'btn-tip-group' }).append(
                $('<div>', { class: 'btn-tip', text: "Trapper" }),
                $('<button>', { class: 'ipe-toolbox-btn fa fa-cub ipe-trapper' }).click(trapper_edit)
            )
        );
    mw.util.addCSS(`
        .ipe-trapper {
            color: #845EC2;
        }
    `);
});