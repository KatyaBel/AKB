let id = null;

$(document).ready(function () {
    getObjects()
    $('#btnAddObj').click(function () {
        openModalCreateObj()
    });
    $('#btnEditObj').click(function () {
        openUpdObjPage()
    });
    $('#btnDelObj').click(function () {
        openModalDelObj()
    });
    $('#addObj').click(function () {
        createObj()
    });
    $('#delObj').click(function () {
        deleteObj(id)
    });
});
function getObjects() {
    $.ajax({
        url: '/get_objects',
        type: 'GET',
        success: function (response) {
            let objs = JSON.parse(response);
            for (let i = 0; i < objs.length; i++) {
                let tr = document.createElement('tr');
                let td1 = document.createElement('td');
                td1.innerHTML = objs[i]['id'];
                tr.appendChild(td1);
                let td2 = document.createElement('td');
                td2.innerHTML = objs[i]['name'];
                tr.appendChild(td2);
                document.getElementById('objTable_body').appendChild(tr);
            }
            tableStyle()
        },
        error: function (error) {
            error = JSON.stringify(error);
            alert('Ошибка: ' + error)
        }
    });
}
function openModalCreateObj() {
    $('#modalAddObj').modal('toggle');
    $('#nameAddObj').val('')
}
function openUpdObjPage() {
    let count = 0, changed_row;
    $('#objTable_body tr').each(function (row) {
        if ($('#objTable_body tr').eq(row).hasClass('table-secondary')) {
            count++;
            changed_row = row
        }
    })
    if (count === 0) {
        alert('Для редактирования выберите объект')
    } else {
        id = $('#objTable_body tr').eq(changed_row).find('td:eq(0)').text()
        window.open('/edit_object/'+id, '_blank')
    }
}
function openModalDelObj() {
    let count = 0, changed_row;
    $('#objTable_body tr').each(function (row) {
        if ($('#objTable_body tr').eq(row).hasClass('table-secondary')) {
            count++;
            changed_row = row
        }
    })
    if (count === 0) {
        alert('Для удаления выберите объект')
    } else {
        $('#modalDelObj').modal('show')
        $('#nameDelObj').text('Удалить объект '+$('#objTable_body tr').eq(changed_row).find('td:eq(1)').text()+
            ' со всеми модулями, устройствами и сигналами?')
        id = $('#objTable_body tr').eq(changed_row).find('td:eq(0)').text()
    }
}

function createObj() {
    let name = $('#nameAddObj').val()
    if (name === '') {
        alert('Заполните все поля')
    } else {
        let my_data = {
            'name': name
        }
        $.ajax({
            url: '/create_object',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(my_data),
            success: function (response) {
                let obj = JSON.parse(response);
                let tr = document.createElement('tr');
                let td1 = document.createElement('td');
                td1.innerHTML = obj['id'];
                tr.appendChild(td1);
                let td2 = document.createElement('td');
                td2.innerHTML = obj['name'];
                tr.appendChild(td2);
                document.getElementById("objTable_body").appendChild(tr);
                tableStyle()
                if ($('#checkOpenEditObj').is(':checked')) {
                    id = obj['id']
                    window.open('/edit_object/'+obj['id'], '_blank')
                }
            },
            error: function (error) {
                error = JSON.stringify(error);
                alert('Ошибка: ' + error)
            }
        })
        $('#modalAddObj').modal('toggle');
    }
}

function deleteObj(id) {
    $.ajax({
        url: '/delete_object/'+id,
        type: 'DELETE',
        success: function (response) {
            let obj = JSON.parse(response);
            if (obj === null) {
                $('#objTable_body tr').each(function (row) {
                    if ($('#objTable_body tr').eq(row).find('td:eq(0)').text() === id) {
                        $('#objTable_body tr').eq(row).remove()
                    }
                })
                tableStyle()
            }
        },
        error: function (error) {
            error = JSON.stringify(error);
            alert('Ошибка: ' + error)
        }
    })
    $('#modalDelObj').modal('toggle');
}

/*
function updateObj(id) {
    let name = $('#fieldUpdateNameObj').val()
    if (name === '') {
        alert('Заполните все поля')
    } else {
        let my_data = {
            'name': name
        }
        $.ajax({
            url: "/obj/" + id,
            type: 'PUT',
            data: JSON.stringify(my_data),
            contentType: false,
            success: function (response) {
                let obj = JSON.parse(response);
                if ('detail' in obj) {
                    alert("Ошибка: " + obj["detail"][0]["msg"])
                } else {
                    let changed_row
                    $('#objTable_body tr').each(function (row) {
                        if ($('#objTable_body tr').eq(row).find('td:eq(0)').text() === obj["id"].toString()) {
                            changed_row = row
                        }
                    })
                    $('#objTable_body tr').eq(changed_row).find("td").eq(0).html(obj["id"]);
                    $('#objTable_body tr').eq(changed_row).find("td").eq(1).html(obj["name"]);
                    tableStyle()
                    setWidthHead()
                }
            },
            error: function (response) {
                document.querySelector('.errorBlock').querySelector('.alertText').textContent = response.responseJSON
                $('.errorBlock').slideDown(500);
                $('.errorBlock').delay(10000).slideUp();

                error = JSON.stringify(error);
                alert('Ошибка: ' + error)
            }
        })
        $('#updateObjModal').modal('toggle');
    }
}*/
function tableStyle() {
    //по нажатию серая подсветка
    $('#objTable_body tr').click(function () {
        $('#objTable_body tr').removeClass("table-secondary");
        $(this).addClass('table-secondary')
    });
}