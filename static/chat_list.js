document.addEventListener('DOMContentLoaded', () => {

    // Conectamos el websocket
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

    // configuramos el boton 
    socket.on('connect', () => {

        // El boton emite el evento 'submit channel'
        document.querySelector('form button').onclick = () => {
            const selection = document.querySelector('form input').value;
            socket.emit('submit channel', {'selection': selection})
        };
    });

     // desactivamos el boton por defecto 
    document.querySelector('form button').disabled = true;
    
    //limpiamos el input inicial para bloquear el boton de crear chat si no hay un chat name
    document.querySelector('form input').value = '';

     // Se habilita el boton si se ingresa un texto en el campo input file
    document.querySelector('form input').onkeyup = () => {
        document.querySelector('form button').disabled = false;
    }

    // Cuando el mensaje se envia, se agrega el nombre a la lista
    socket.on ('cast channel', data => {
        const li = document.createElement('li');

        // Se usa innerHTML 
        li.innerHTML = `<a href="/chatrooms/${data["chat_id"]}"> ${data["selection"]} </a>`;
        console.log(li.innerHTML);
        document.querySelector('#chatrooms').append(li);

        //limpiamos el input y desactivamos el boton nuevamente
        document.querySelector('form input').value = '';
        document.querySelector('form button').disabled = true;
    
    });

        
});
