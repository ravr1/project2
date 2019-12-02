document.addEventListener('DOMContentLoaded', () => {

    // Abrimos un request para obtener los mensajes previos
    const request = new XMLHttpRequest();
    request.open("POST", "/listmessages");


    request.onload = () => {
        //Obtenemos los datos 
        const data = JSON.parse(request.responseText);
        // usamos el id para identificar los mensajes
        localStorage.setItem("chat_id", data["chat_id"])
        let i;
  
        //creamos una lista por mensaje contenido en la lista de mensajes
        for ( i=0; i<data["message"].length; i++) {
            const li = document.createElement('li');
            const response = data["message"][i];

            //creamos un contador para saber cuantos mensajes tenemos 
      
            document.querySelector('#count').innerHTML = data["message"].length;
      
            // Usamos innerHTML para acceder a las propiedades del html
            li.innerHTML =  `</small> <strong>${response["user_name"]}</strong> : <span class="mx-4">${response["selection"]}</span> <small>${response["time"]}</small>`;
            document.querySelector('#messages').append(li);
        }
    };
    request.send();



    // nos conectamos con el websocket
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

    
    // desactivamos el boton por defecto 
    document.querySelector('button').disabled = true;
    // Se habilita el boton si se ingresa un texto en el campo input file
    document.querySelector('input').onkeyup = () => {
        document.querySelector('button').disabled = false;
    }

    // Configuramos el boton
    socket.on('connect', () => {

       
        // el boton emite el evento 'submit message' 
        document.querySelector('button').onclick = function () {
            const selection = document.querySelector('input').value;
            this.form.reset();
            socket.emit('submit message', {'selection': selection});
        };

        
    });



    // cuando el mensaje se envia, lo añadimos a la lista
    socket.on ('cast message', data => {
        
        
        if (data["chat_id"] === localStorage.chat_id) {
            const li = document.createElement('li');

            // usamos innerHTML ipara acceder al html
            li.innerHTML = ` <strong>${data["user_name"]}</strong> : <span class="mx-4">${data["selection"]}</span> <small>${data["time"]}</small>`;
            document.querySelector('#messages').append(li);

            //limpiamos el input y desactivamos el boton nuevamente
            document.querySelector('input').value = '';
            document.querySelector('button').disabled = true;
    

    
        }
    });


});
