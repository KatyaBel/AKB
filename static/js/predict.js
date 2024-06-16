$(document).ready(function () {
    getObjects()
    let selObjs = document.getElementById('selectObjs');
    $('#selectObjs').on('change', function () {
        getDevices(selObjs.value)
    })
    $('#start').on('click', function () {
        let device_id = document.getElementById('selectDevs').value
        let start_date = document.getElementById('start_date').value
        let start_time = document.getElementById('start_time').value
        let period = document.getElementById('period_time').value
        if (start_date === '' || start_time === '' || period === '') {
            alert('Заполните все поля диапазона прогнозирования')
        } else {
            let user_date = start_date+'T'+start_time
            $.ajax({
                url: '/get_last_signal/'+device_id,
                type: 'GET',
                success: function (response) {
                    let base_date = JSON.parse(response);
                    if (user_date <= base_date) {
                        alert('Дата старта должна быть позднее последнего сигнала с этого устройства')
                    } else if (new Date('1970-01-01T'+period).getSeconds() % 10 !== 0) {
                        alert('Период должен быть кратен 10 секундам')
                    } else if (period < '00:00:10') {
                        alert('Период не может быть меньше 10 секунд')
                    } else {
                        predict(device_id, start_date+' '+start_time, period)
                    }
                },
                error: function (error) {
                    error = JSON.stringify(error);
                    alert('Ошибка: ' + error)
                }
            });
        }
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
            let selDevs = document.getElementById('selectDevs');
            while (selDevs.firstChild) {
                selDevs.removeChild(selDevs.lastChild);
            }
            for (let i = 0; i < devs.length; i++) {
                let optDev = document.createElement('option');
                optDev.value = devs[i]['id'];
                optDev.innerHTML = devs[i]['name'];
                selDevs.appendChild(optDev);
            }
        },
        error: function (error) {
            error = JSON.stringify(error);
            alert('Ошибка: ' + error)
        }
    });
}

function predict(num, start_date, period) {
    document.getElementById('nameDev').innerText = $('#selectDevs option:selected').html();
    $.ajax({
        url: '/get_predict_v/'+num+'/'+'/'+period,
        type: 'GET',
        success: function (response) {
            let data = JSON.parse(response);
            $.ajax({
                url: '/get_limits/'+num,
                type: 'GET',
                success: function (response) {
                    /*let params = JSON.parse(response);
                    let title = data['f_title']

                    let r = /[\d|.]+/g;
                    let m;
                    while ((m = r.exec(title)) != null) {
                        if (m[0].indexOf('.') >= 0) {
                            let num_arr = m[0].split('.');
                            title = title.replace(m[0], num_arr[0]+','+num_arr[1].substring(0, 5))
                        }
                    }
                    while (title.indexOf('e') >= 0) {
                        title = title.replace('e', '*10^')
                    }
                    while (title.indexOf('**') >= 0) {
                        title = title.replace('**', '^')
                    }*/
                    let x_str = data['x']
                    let x = []
                    for (let i = 0; i < x_str.length; i++) {
                        let date = new Date(x_str[i]);
                        let new_date = date.getDate()+'.'+date.getMonth()+'.'+date.getFullYear()+' '+date.getHours()+':'+date.getMinutes()+':'+date.getSeconds()
                        x.push(new_date)
                    }
                    let y = JSON.parse(data['y'])
                    let f = JSON.parse(data['f'])

                    if (num === '1') {
                        drawChart('График', x, y, f, 11.0, 14.5, 'canvas1')
                    } else {
                        //drawChart(title, x, y, f, params[0]['min_v'], params[0]['max_v'], 'canvas1')
                    }



                    let x_p_str = data['x_p']
                    let x_p = []
                    for (let i = 0; i < x_p_str.length; i++) {
                        let date = new Date(x_p_str[i]);
                        let new_date = date.getDate()+'.'+date.getMonth()+'.'+date.getFullYear()+' '+date.getHours()+':'+date.getMinutes()+':'+date.getSeconds()
                        x_p.push(new_date)
                    }
                    let y_p = JSON.parse(data['y_p'])
                    drawPredict(x_p, y_p, 11, 14.5, 'calcCanvas1')
                },
                error: function (error) {
                    error = JSON.stringify(error);
                    alert('Ошибка: ' + error)
                }
            })
        },
        error: function (error) {
            error = JSON.stringify(error);
            alert('Ошибка: ' + error)
        }
    });

    /*
    $.ajax({
        url: '/get_predict_t/'+num+'/'+start_date+'/'+period,
        type: 'GET',
        success: function (response) {
            let data = JSON.parse(response);
            $.ajax({
                url: '/get_limits/'+num,
                type: 'GET',
                success: function (response) {
                    let params = JSON.parse(response);
                    let title = data['f_title']
                    let x_str = data['x']
                    let x = []
                    for (let i = 0; i < x_str.length; i++) {
                        let date = new Date(x_str[i]);
                        let new_date = date.getDate()+'.'+date.getMonth()+'.'+date.getFullYear()+' '+date.getHours()+':'+date.getMinutes()+':'+date.getSeconds()
                        x.push(new_date)
                    }
                    let y = JSON.parse(data['y'])
                    let f = JSON.parse(data['f'])
                    drawChart(title, x, y, f, params[0]['min_t'], params[0]['max_t'], 'canvas2')
                    let x_p_str = data['x_p']
                    let x_p = []
                    for (let i = 0; i < x_p_str.length; i++) {
                        let date = new Date(x_p_str[i]);
                        let new_date = date.getDate()+'.'+date.getMonth()+'.'+date.getFullYear()+' '+date.getHours()+':'+date.getMinutes()+':'+date.getSeconds()
                        x_p.push(new_date)
                    }
                    let y_p = JSON.parse(data['y_p'])
                    drawPredict(x_p, y_p, params[0]['min_t'], params[0]['max_t'], 'calcCanvas2')
                },
                error: function (error) {
                    error = JSON.stringify(error);
                    alert('Ошибка: ' + error)
                }
            })
        },
        error: function (error) {
            error = JSON.stringify(error);
            alert('Ошибка: ' + error)
        }
    });
    */
}

function drawChart(func, x, y, f, max, min, chart_id) {
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
                    label: 'Исходные данные',
                    data: y,
                    lineTension: 0,
                    fill: false,
                    borderColor: cur_color,
                    borderWidth: 0,
                    pointBackgroundColor: cur_color,
                    pointRadius: 0,
                    pointHoverRadius: 0
                },
                {
                    label: func,
                    data: f,
                    lineTension: 0,
                    fill: false,
                    borderDash: [5, 5],
                    borderColor: '#6B8E23',
                    borderWidth: 0,
                    pointBackgroundColor: '#6B8E23',
                    pointRadius: 0,
                    pointHoverRadius: 0
                },
                {
                    label: 'Max',
                    data: y1,
                    lineTension: 0,
                    fill: false,
                    borderColor: '#DC143C',
                    borderWidth: 1,
                    pointRadius: 0,
                    pointHoverRadius: 0
                },
                {
                    label: 'Min',
                    data: y2,
                    lineTension: 0,
                    fill: false,
                    borderColor: '#DC143C',
                    borderWidth: 1,
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

function drawPredict(x, y, max, min, chart_id) {
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
                    label: 'Predict',
                    data: y,
                    lineTension: 0,
                    fill: false,
                    borderColor: 'orange',
                    borderWidth: 1,
                    pointBackgroundColor: 'orange',
                    pointRadius: 0,
                    pointHoverRadius: 0
                },
                {
                    label: 'Max',
                    data: y1,
                    lineTension: 0,
                    fill: false,
                    borderColor: '#DC143C',
                    borderWidth: 1,
                    pointRadius: 0,
                    pointHoverRadius: 0
                },
                {
                    label: 'Min',
                    data: y2,
                    lineTension: 0,
                    fill: false,
                    borderColor: '#DC143C',
                    borderWidth: 1,
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