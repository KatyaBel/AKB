$(document).ready(function () {
    getObjects()
    let selObjs = document.getElementById('selectObjs');
    $('#selectObjs').on('change', function () {
        getDevices(selObjs.value)
    })
    $('#checkAll').on('click', function () {
        $('#ulDevs input:checkbox').each(function() {
            $(this).prop('checked', true)
        });
    })
    $('#uncheckAll').on('click', function () {
        $('#ulDevs input:checkbox').each(function() {
            $(this).prop('checked', false)
        });
    })
    $('#start').on('click', function () {
        let devices = [];
        $('#ulDevs input:checkbox[type=checkbox]:checked').each(function() {
            devices.push($(this).attr('id').substring(2))
        });
        let start_date = document.getElementById('start_date').value
        let start_time = document.getElementById('start_time').value
        let end_date = document.getElementById('end_date').value
        let end_time = document.getElementById('end_time').value
        if (start_date === '' || start_time === '' || end_date === '' || end_time === '') {
            alert('Заполните все поля диапазона времени')
        } else {
            createTabs(devices, start_date+' '+start_time+'/'+end_date+' '+end_time)
        }
    })
    $('#ulTabs a').on('click', function () {
        $(this).tab('show');
    })
});

function getObjects() {
    $.ajax({
        url: '/get_objects',
        type: 'GET',
        success: function (response) {
            let objs = JSON.parse(response);
            let selObjs = document.getElementById('selectObjs');
            for (let i = 0; i < objs.length; i++) {
                let optObj = document.createElement('option');
                optObj.value = objs[i]['id'];
                optObj.innerHTML = objs[i]['name'];
                selObjs.appendChild(optObj);
            }
            getDevices(selObjs.value);
        },
        error: function (error) {
            error = JSON.stringify(error);
            alert('Ошибка: ' + error)
        }
    });
}

function getDevices(num) {
    $.ajax({
        url: '/get_devices/'+num,
        type: 'GET',
        success: function (response) {
            let devs = JSON.parse(response);
            let ulDevs = document.getElementById('ulDevs');
            while (ulDevs.firstChild) {
                ulDevs.removeChild(ulDevs.lastChild);
            }
            for (let i = 0; i < devs.length; i++) {
                let liDev = document.createElement('li');
                liDev.setAttribute('class','list-group-item');

                let inputDev = document.createElement('input');
                inputDev.setAttribute('class','form-check-input me-2');
                inputDev.setAttribute('checked', true)
                inputDev.type = 'checkbox'
                inputDev.id = 'ch'+devs[i]['id'];
                liDev.appendChild(inputDev);

                let labelDev = document.createElement('label');
                labelDev.setAttribute('class','form-check-label');
                labelDev.htmlFor = 'ch'+devs[i]['id'];
                labelDev.innerHTML = devs[i]['name'];
                liDev.appendChild(labelDev);

                ulDevs.appendChild(liDev);
            }
        },
        error: function (error) {
            error = JSON.stringify(error);
            alert('Ошибка: ' + error)
        }
    });
}

function createTabs(devices, date) {
    let ulTabs = document.getElementById('ulTabs');
    let tabCont = document.getElementById('tabCont')
    while (ulTabs.firstChild) {
        ulTabs.removeChild(ulTabs.lastChild);
    }
    while (tabCont.firstChild) {
        tabCont.removeChild(tabCont.lastChild);
    }
    for (let i = 0; i < devices.length; i++) {
        let newTab = document.createElement('li');
        let linkTab = document.createElement('a');

        let divTab = document.createElement('div');
        let divCar = document.createElement('div')
        let divCarIn = document.createElement('div')
        let butPrev = document.createElement('button')
        let butNext = document.createElement('button')
        let arrowPrev = document.createElement('div')
        let arrowNext = document.createElement('div')

        if (i === 0) {
            linkTab.setAttribute('class', 'nav-link active');
            divTab.setAttribute('class', 'tab-pane fade active show')
        } else {
            linkTab.setAttribute('class', 'nav-link');
            divTab.setAttribute('class', 'tab-pane fade')
        }
        divTab.id = 'dev'+devices[i]
        linkTab.href = '#' + divTab.id;
        linkTab.textContent = $("label[for='ch"+devices[i]+"']")[0].innerHTML
        linkTab.setAttribute('data-bs-toggle', 'tab')

        newTab.appendChild(linkTab);
        ulTabs.appendChild(newTab);

        divCar.id = 'carousel'+devices[i]
        divCar.setAttribute('class', 'carousel slide')
        divCar.setAttribute('data-bs-theme', 'dark')

        divCarIn.setAttribute('class', 'carousel-inner')

        let divCarItem = [document.createElement('div'), document.createElement('div')];
        let canvas = [document.createElement('canvas'), document.createElement('canvas')]

        divCarItem[0].setAttribute('class', 'carousel-item active')
        canvas[0].id = 'canvas'+(2*(i+1)-1)
        divCarItem[0].appendChild(canvas[0])
        divCarItem[1].setAttribute('class', 'carousel-item')
        canvas[1].id = 'canvas'+(2*(i+1))
        divCarItem[1].appendChild(canvas[1])

        divCarIn.appendChild(divCarItem[0])
        divCarIn.appendChild(divCarItem[1])

        butPrev.setAttribute('class', 'carousel-control-prev')
        butPrev.type = 'button'
        butPrev.setAttribute('data-bs-target', '#'+divCar.id)
        butPrev.setAttribute('data-bs-slide', 'prev')
        arrowPrev.setAttribute('class', 'carousel-control-prev-icon')
        arrowPrev.setAttribute('aria-hidden', 'true')
        butPrev.appendChild(arrowPrev)

        butNext.setAttribute('class', 'carousel-control-next')
        butNext.type = 'button'
        butNext.setAttribute('data-bs-target', '#'+divCar.id)
        butNext.setAttribute('data-bs-slide', 'next')
        arrowNext.setAttribute('class', 'carousel-control-next-icon')
        arrowNext.setAttribute('aria-hidden', 'true')
        butNext.appendChild(arrowNext)

        divCar.appendChild(divCarIn)
        divCar.appendChild(butPrev)
        divCar.appendChild(butNext)

        divTab.appendChild(divCar)
        tabCont.appendChild(divTab)

        $.ajax({
            url: '/get_limits/'+devices[i],
            type: 'GET',
            success: function (response) {
                let params = JSON.parse(response);
                let x1 = []
                let y1 = []
                $.ajax({
                    url: '/get_signals_v/'+devices[i]+'/'+date,
                    type: 'GET',
                    success: function (response) {
                        let signals = JSON.parse(response);
                        for (let i = 0; i < signals.length; i++) {
                            let date = new Date(signals[i]['time']);
                            let new_date = date.getDate()+'.'+date.getMonth()+'.'+date.getFullYear()+' '+date.getHours()+':'+date.getMinutes()+':'+date.getSeconds()
                            x1.push(new_date)
                            y1.push(signals[i]['value'])
                        }

                        if (devices[i] === '1') {
                            drawChart('Напряжение', x1, y1, 11, 14.5, canvas[0].id)
                        } else {
                            drawChart('Напряжение', x1, y1, params[0]['min_v'], params[0]['max_v'], canvas[0].id)
                        }


                    },
                    error: function (error) {
                        error = JSON.stringify(error);
                        alert('Ошибка: ' + error)
                    }
                });
                let x2 = []
                let y2 = []
                $.ajax({
                    url: '/get_signals_t/'+devices[i]+'/'+date,
                    type: 'GET',
                    success: function (response) {
                        let signals = JSON.parse(response);
                        for (let i = 0; i < signals.length; i++) {
                            let date = new Date(signals[i]['time']);
                            let new_date = date.getDate()+'.'+date.getMonth()+'.'+date.getFullYear()+' '+date.getHours()+':'+date.getMinutes()+':'+date.getSeconds()
                            x2.push(new_date)
                            y2.push(signals[i]['value'])
                        }
                        drawChart('Температура', x2, y2, params[0]['min_t'], params[0]['max_t'], canvas[1].id)
                    },
                    error: function (error) {
                        error = JSON.stringify(error);
                        alert('Ошибка: ' + error)
                    }
                });
            },
            error: function (error) {
                error = JSON.stringify(error);
                alert('Ошибка: ' + error)
            }
        })
    }
}

function drawChart(title, x, y, min, max, chart_id) {
    let cur_color;
    if ((chart_id.substring(6) % 2) === 1) {
        cur_color = '#4682B4'
    } else {
        cur_color = '#FF7F50'
    }
    let y1 =[]
    let y2 =[]
    for(let i = 0; i < y.length; i++) {
        y1.push(max)
        y2.push(min)
    }
    let chx = document.getElementById(chart_id).getContext("2d");
    let data =
        {
            labels: x,
            datasets: [
                {
                    label: title,
                    data: y,
                    lineTension: 0,
                    fill: false,
                    borderColor: cur_color,
                    borderWidth: 1,
                    pointBackgroundColor: cur_color,
                    pointRadius: 3,
                    pointHoverRadius: 5
                },
                {
                    label: 'Max',
                    data: y1,
                    lineTension: 0,
                    fill: false,
                    borderColor: '#DC143C',
                    borderWidth: 2,
                    pointRadius: 0,
                    pointHoverRadius: 0
                },
                {
                    label: 'Min',
                    data: y2,
                    lineTension: 0,
                    fill: false,
                    borderColor: '#DC143C',
                    borderWidth: 2,
                    pointRadius: 0,
                    pointHoverRadius: 0
                }
            ]
        };
    let options =
        {
            legend: {
                display: true,
                position: 'top',
                labels: {
                    boxWidth: 20,
                    fontColor: 'black'
                }
            },
        };
    new Chart(chx, {
        type: 'line',
        data: data,
        options: options
    });
}