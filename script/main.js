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
    let formData = new FormData();
    formData.append("pagetext", pagetext)
    // console.log(pagetext)
    const requestOptions = {
        method: "POST",
        body: formData,
        referrerPolicy: "no-referrer-when-downgrade",
        mode: "cors"
    };
    await fetch(`https://trapper-script.gugumur.eu.org/main`, requestOptions)
        .then(response => {
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                return response.json();
            } else {
                return response.text();
            }
        }).then((data) => {
            InPageEdit.progress(true);
            setTimeout(() => { InPageEdit.progress(false) }, 500);
            if (typeof data === 'object') {
                console.log(data)
                if (data["status"] == true) {
                    ssi_modal.notify('success', {
                        className: 'in-page-edit',
                        title: "获取更新后的内容成功！",
                        content: data.hint,
                    })
                    $('.editArea').val(data.text)
                    $('#editSummary').val("//Powered by InPageEdit & Trapper Script")
                }
                else {
                    if (data["text"] != "") {
                        ssi_modal.notify('error', {
                            className: 'in-page-edit',
                            title: '该页面似乎不需要Trapper的更新？',
                            content: data.hint,
                        });
                    }
                }
            }
            else {
                ssi_modal.notify('error', {
                    className: 'in-page-edit',
                    title: 'Vercel服务器超时了...',
                    content: "呜呜呜",
                });
            }
        })
        .catch(e => {
            InPageEdit.progress(true);
            setTimeout(function () {
                InPageEdit.progress(false);
            }, 500);
            console.error('Error:', e);
            ssi_modal.notify('error', {
                className: 'in-page-edit',
                title: 'Trapper处理出错！',
                content: e,
            });
        })
}
async function trapper_edit() {
    const title = mw.config.get("wgPageName")
    InPageEdit.quickEdit({
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
