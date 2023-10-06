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
    let pagetext = await get_page_text()
    // console.log(pagetext)
    const requestOptions = {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ "pagetext": pagetext })
    };
    console.log(requestOptions)
    await fetch(`https://trapper-script.gudev.online/main`, requestOptions)
        .then((response) => response.json())
        .then((data) => {
            InPageEdit.progress(true);
            setTimeout(function () {
                InPageEdit.progress(false);
            }, 500);
            let hint = ""
            if (data.hint) {
                hint = "可能还需要注意以下内容" + data.hint
            }
            else {
                hint = ""
            }
            if (data["status"] == true) {
                ssi_modal.notify('success', {
                    className: 'in-page-edit',
                    title: "获取更新后的内容成功！",
                    content: hint,
                })
                $('.editArea').val(data.text)
                $('#editSummary').val("//Powered by InPageEdit & Trapper Script")
            }
            else {
                if (data["text"] != "") {
                    ssi_modal.notify('error', {
                        className: 'in-page-edit',
                        title: '该页面似乎不需要Trapper的更新？',
                        content: hint,
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
            return { "status": false, "text": "", "hint": "" }
        })
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
        InPageEdit.progress('正在加载Trapper......');
        await get_data();
    } catch (error) {
        console.error('Error:', error);
    }
}

mw.hook('InPageEdit.toolbox').add(({ $toolbox }) => {
    $toolbox
        .find('.btn-group.group1')
        .append(
            $('<li>', { class: 'btn-tip-group' }).append(
                $('<div>', { class: 'btn-tip', text: "Trapper" }),
                $('<button>',
                    {
                        id: "trapper-btn",
                        class: 'ipe-toolbox-btn fa fa-cube ipe-trapper'
                    })
                    .click(trapper_edit)
            )
        );
    mw.util.addCSS(`
        #trapper-btn {
            background: #845EC2 !important;
        }
    `);
});