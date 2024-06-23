const volt_color = '#4682B4'
const temp_color = '#FF7F50'
const inter_color = '#A52A2A'
$(document).ready(function () {
    getObjects()
    $('#selectObjs').on('change', function () {
        let selObjs = document.getElementById('selectObjs');
        getDevices(selObjs.value)
    })
    $('#selectDevs').on('change', function () {
        let selDevs = document.getElementById('selectDevs');
        setLastSignal(selDevs.value)
    })
    $('#start').on('click', function () {
        let device_id = document.getElementById('selectDevs').value
        let period = document.getElementById('period_time').value
        if (period === '') {
            alert('Выберите период')
        } else if (period.slice(6) % 30 !== 0) {
            alert('Период должен быть кратен 30 минутам')
        } else if (period < '00:00:30') {
            alert('Период не может быть меньше 30 минут')
        } else {
            predict(device_id, period)
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
            setLastSignal(selDevs.value)
        },
        error: function (error) {
            error = JSON.stringify(error);
            alert('Ошибка: ' + error)
        }
    });
}

function setLastSignal(num) {
    $.ajax({
        url: '/get_last_signal/'+num,
        type: 'GET',
        success: function (response) {
            let signal = JSON.parse(response);
            let date = new Date(signal);
            let new_date = date.getDate()+'.'+(date.getMonth()+1)+'.'+date.getFullYear()+' '+date.getHours()+':'+date.getMinutes()+':'+date.getSeconds()
            $('#start_date').val(new_date)
        },
        error: function (error) {
            error = JSON.stringify(error);
            alert('Ошибка: ' + error)
        }
    });
}

function predict(num, period) {
    document.getElementById('nameDev').innerText = $('#selectDevs option:selected').html();
    $.ajax({
        url: '/get_predict_v/'+num+'/'+period,
        type: 'GET',
        success: function (response) {
            let data = JSON.parse(response);
            $.ajax({
                url: '/get_limits/'+num,
                type: 'GET',
                success: function (response) {
                    let params = JSON.parse(response);
                    let title1 = data['f1_title']
                    let title2 = data['f2_title']
                    let r = /[\d|.]+/g;
                    let m;
                    while ((m = r.exec(title1)) != null) {
                        if (m[0].indexOf('.') >= 0) {
                            let num_arr = m[0].split('.');
                            title1 = title1.replace(m[0], num_arr[0]+','+num_arr[1].substring(0, 5))
                        }
                    }
                    while ((m = r.exec(title2)) != null) {
                        if (m[0].indexOf('.') >= 0) {
                            let num_arr = m[0].split('.');
                            title2 = title2.replace(m[0], num_arr[0]+','+num_arr[1].substring(0, 5))
                        }
                    }
                    while (title1.indexOf('e') >= 0) {
                        title1 = title1.replace('e', '*10^')
                    }
                    while (title2.indexOf('e') >= 0) {
                        title2 = title2.replace('e', '*10^')
                    }
                    while (title1.indexOf('**') >= 0) {
                        title1 = title1.replace('**', '^')
                    }
                    while (title2.indexOf('**') >= 0) {
                        title2 = title2.replace('**', '^')
                    }
                    title1 = 'Заряд: '+title1.substring(0, title1.length-8)
                    title2 = 'Разряд: '+title2.substring(0, title2.length-8)
                    $('#charge_f').text(title1)
                    $('#discharge_f').text(title2)
                    let x_str = data['x']
                    let x = []
                    for (let i = 0; i < x_str.length; i++) {
                        let date = new Date(x_str[i]);
                        let new_date = date.getDate()+'.'+(date.getMonth()+1)+'.'+date.getFullYear()+' '+date.getHours()+':'+date.getMinutes()+':'+date.getSeconds()
                        x.push(new_date)
                    }
                    let y = JSON.parse(data['y'])
                    let f = JSON.parse(data['f'])
                    drawChart(x, y, f, params[0]['min_v'], params[0]['max_v'], 'canvas1')
                    let x_p_str = data['x_p']
                    let x_p = []
                    for (let i = 0; i < x_p_str.length; i++) {
                        let date = new Date(x_p_str[i]);
                        let new_date = date.getDate() + '.' + (date.getMonth() + 1) + '.' + date.getFullYear() + ' ' + date.getHours() + ':' + date.getMinutes() + ':' + date.getSeconds()
                        x_p.push(new_date)
                    }
                    let y_p = JSON.parse(data['y_p'])
                    drawPredict(x_p, y_p, params[0]['min_v'], params[0]['max_v'], 'calcCanvas1')
                    /*
                    let x_p_c = data['x_p_c'].toString().split('.')
                    $.ajax({
                        url: '/get_predict_t/'+num+'/['+x_p_c+']/['+y_p+']',
                        type: 'GET',
                        success: function (response) {
                            let data = JSON.parse(response);
                            $.ajax({
                                url: '/get_limits/'+num,
                                type: 'GET',
                                success: function (response) {
                                    let params = JSON.parse(response);
                                    let x_str = data['x']
                                    let x = []
                                    for (let i = 0; i < x_str.length; i++) {
                                        let date = new Date(x_str[i]);
                                        let new_date = date.getDate()+'.'+(date.getMonth()+1)+'.'+date.getFullYear()+' '+date.getHours()+':'+date.getMinutes()+':'+date.getSeconds()
                                        x.push(new_date)
                                    }
                                    let y = JSON.parse(data['y'])
                                    let f = []
                                    drawChart(title, x, y, f, params[0]['min_t'], params[0]['max_t'], 'canvas2')
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
}

function drawChart(x, y, f, max, min, chart_id) {
    let cur_color;
    if ((chart_id.substring(6) % 2) === 1) {
        cur_color = volt_color
    } else {
        cur_color = temp_color
        func = ''
    }
    let y1 =[]
    let y2 =[]
    for(let i = 0; i < y.length; i++) {
        y1.push(max)
        y2.push(min)
    }
    let y_step
    if ((chart_id.substring(6) % 2) === 1) {
        y_step = 0.5
    } else {
        y_step = 5
    }
    let chx = document.getElementById(chart_id).getContext("2d");
    let data =
        {
            labels: x,
            datasets: [
                {
                    label: '',
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
                    label: 'func',
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
                    label: '',
                    data: y1,
                    lineTension: 0,
                    fill: false,
                    borderColor: inter_color,
                    borderWidth: 0,
                    pointRadius: 0,
                    pointHoverRadius: 0
                },
                {
                    label: '',
                    data: y2,
                    lineTension: 0,
                    fill: false,
                    borderColor: inter_color,
                    borderWidth: 0,
                    pointRadius: 0,
                    pointHoverRadius: 0
                }
            ]
        };
    let options =
        {
            legend: {
                display: false
            },
            scales: {
                yAxes: [{
                    ticks: {
                        stepSize: y_step
                    }
                }],
                xAxes: [{
                    ticks: {
                        beginAtZero: true,
                        maxTicksLimit: 20
                    }
                }]
            }
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
    let y_step
    if ((chart_id.substring(10) % 2) === 1) {
        y_step = 0.5
    } else {
        y_step = 5
    }
    let chx = document.getElementById(chart_id).getContext("2d");
    let data =
        {
            labels: x,
            datasets: [
                {
                    label: '',
                    data: y,
                    lineTension: 0,
                    fill: false,
                    borderColor: 'orange',
                    borderWidth: 0,
                    pointBackgroundColor: 'orange',
                    pointRadius: 0,
                    pointHoverRadius: 0
                },
                {
                    label: '',
                    data: y1,
                    lineTension: 0,
                    fill: false,
                    borderColor: inter_color,
                    borderWidth: 0,
                    pointRadius: 0,
                    pointHoverRadius: 0
                },
                {
                    label: '',
                    data: y2,
                    lineTension: 0,
                    fill: false,
                    borderColor: inter_color,
                    borderWidth: 0,
                    pointRadius: 0,
                    pointHoverRadius: 0
                }
            ]
        };
    let options =
        {
            legend: {
                display: false
            },
            scales: {
                yAxes: [{
                    ticks: {
                        stepSize: y_step
                    }
                }],
                xAxes: [{
                    ticks: {
                        beginAtZero: true,
                        maxTicksLimit: 20
                    }
                }]
            }
        };
    new Chart(chx, {
        type: 'line',
        data: data,
        options: options
    });
}