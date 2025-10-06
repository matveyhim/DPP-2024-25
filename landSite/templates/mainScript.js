var myMap, myPlacemark, coords;
ymaps.ready(init);
function init () {

    //Определяем начальные параметры карты
    myMap = new ymaps.Map('YMapsID', {
            center: [66.666666, 66.666666], 
            zoom: 10, 
            behaviors: ['default', 'scrollZoom']
    });	
    
    //Определяем элемент управления поиск по карте	
    var SearchControl = new ymaps.control.SearchControl({noPlacemark:true});	

    //Добавляем элементы управления на карту
    myMap.controls
        .add(SearchControl)                
        .add('zoomControl')                
        .add('typeSelector')                 
        .add('mapTools');
        
    coords = [44.444444, 44.444444];
    
    //Определяем метку и добавляем ее на карту				
    myPlacemark = new ymaps.Placemark([55.555555, 55.555555],{}, {preset: "twirl#redIcon", draggable: true});	
    
    myMap.geoObjects.add(myPlacemark);			

    //Отслеживаем событие перемещения метки
    myPlacemark.events.add("dragend", function (e) {			
        coords = this.geometry.getCoordinates();
        savecoordinats();
    }, myPlacemark);

    //Отслеживаем событие щелчка по карте
    myMap.events.add('click', function (e) {        
        coords = e.get('coordPosition');
        savecoordinats();
    });	

    //Отслеживаем событие выбора результата поиска
    SearchControl.events.add("resultselect", function (e) {
        coords = SearchControl.getResultsArray()[0].geometry.getCoordinates();
        savecoordinats();
    });
    
    //Ослеживаем событие изменения области просмотра карты - масштаб и центр карты
    myMap.events.add('boundschange', function (event) {
    if (event.get('newZoom') != event.get('oldZoom')) {		
        savecoordinats();
    }
    if (event.get('newCenter') != event.get('oldCenter')) {		
        savecoordinats();
    }
    
    });
    
}

//Функция для передачи полученных значений в форму
function savecoordinats (){	
    var new_coords = [coords[0].toFixed(4), coords[1].toFixed(4)];	
    var lat = coords[0].toFixed(4);	
    var lon = coords[1].toFixed(4);
    myPlacemark.getOverlay().getData().geometry.setCoordinates(new_coords);
    document.getElementById("lat").value = lat;
    document.getElementById("lon").value = lon;
}
function save(){
    const url='/save/';
    const hInput=document.getElementById('h');
    const horInput=document.getElementById('hor');
    const MhInput=document.getElementById('Mh');
    lat = coords[0].toFixed(4);	//lat.value;
    lon = coords[1].toFixed(4);//lon.value;
    h = hInput.value;
    hor = horInput.value;
    Mh = MhInput.value;

    let data={lat:lat, lon:lon, alt:h, hor:hor, Mh:Mh};

    let fetchData={
        method:'POST',
        body: JSON.stringify(data),
        headers: new Headers({
        'Content-Type':'application/json; charset=UTF-8'
        })
    }
    fetch(url,fetchData)
        .then(function(){
    })
}				