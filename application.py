import os

from datetime import datetime
from flask import Flask, render_template, session, request, redirect, url_for, jsonify
from flask_session import Session
from flask_socketio import SocketIO, emit

app = Flask(__name__)

# configuracion de sesion para filesystem 
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
socketio = SocketIO(app)


chatlist = []  # lista de chats
usernames = []  # lista de usuarios activos
messagedict = {}  # mensajes de usuarios y hora de envio.



@app.route("/")
def index():
 
    if "user_name" in session:

        # redirecciona al usuario al ultimo chat ingresado antes de salir
        if "chat_id" in session:
            if len(chatlist) >= session["chat_id"]:
                return redirect(url_for('chatroom', chat_id=session["chat_id"]))

        #si no, se redirecciona al chat main
        return redirect(url_for('chatmain'))
    #si el usuario no se encuentra en la session, regresa al "registro"
    return render_template("index.html")


# pagina principal donde se muetran todos los chats
@app.route("/chatmain", methods=["GET", "POST"])
def chatmain():

    if request.method == "POST":
        
        #DISPLAY NAME
        user_name = request.form.get("user_name")
        # si el nombre de usuario ya se encunetra en el array usernames se redirecciona a la pagina de error
        if user_name in usernames and user_name is not "":
            return render_template("error.html", error_message="El nombre de usuario ya existe")
        # de lo contrario se añade el usuario al array
        usernames.append(user_name)
        session["user_name"] = user_name

    # se revisa si el usuario esta en session
    if request.method=="GET" and "user_name" not in session:
        return render_template("error.html", error_message="Por favor inicia sesion")

    # se da inicio a la pag de inicio y se manda el nombre de usuario y la lista de chats disponibles
    return render_template("chatmain.html", chatlist=chatlist, user_name=session["user_name"])


@app.route("/logout", methods=["GET"])
def logout():
    # elimina el nombre de usuario del array usernames y de la sesion. 
    try:
        out = session.pop("user_name")
    except KeyError:
        return render_template("error.html", error_message="Por favor inicia sesion")
    else:
        usernames.remove(out)
    # se redirecciona a la pagina inicial 
    return redirect(url_for('index'))



@app.route("/chatrooms/<int:chat_id>", methods=["GET", "POST"])
def chatroom(chat_id):

    chatroom_name = request.form.get("chatroom_name")
    if request.method == "POST":
        
        #si la sala de chat ya existe, se desplega un mensaje de error.
        if chatroom_name in chatlist:
            return render_template("error.html", error_message="La sala de chat ya existe")

        # Si la sala no existe, esta se agrega al array chatlist
        chatlist.append(chatroom_name)
        messagedict[chatroom_name] = []

 
    if request.method == "GET":
        
       # se revisa si el usuario esta logeado
        if "user_name" not in session:
            return render_template("error.html", error_message="Por favor iniciar sesion")
        # se revisa si la sala de chat existe chat 
        if len(chatlist) < chat_id:
            return render_template("error.html", error_message="La sala de chat no existe!")

    # Se añade el canal actual a la sesion del usuario 
    session["chat_id"] = chat_id
     
    return render_template("chatroom.html", user_name=session["user_name"], chat_name=chatlist[chat_id-1])


##################################################################
# Socket io // mensajes para las salas de chat
@socketio.on("submit message")
def message(data):
    selection = data["selection"]
    time = datetime.now().strftime("%Y-%m-%d %H:%M")  # almacenamos la hora actual

    # formato del mensaje enviado
    response_dict = {"selection": selection, "time": time, "user_name": session["user_name"]}
    messagelist = messagedict[chatlist[session["chat_id"] - 1]]

    # si la lista de mensajes llega a 100 se elimina el primero, asi solo almacenamos 100 mensajes
    if len(messagelist) == 100:
        del messagelist[0]

    # añadimos los nuevos mensajes al canal actual
    messagelist.append(response_dict)
    emit("cast message", {**response_dict, **{"chat_id": str(session["chat_id"])}}, broadcast=True)


# retornamos los mensajes del chatroom usando Ajax request junto al chat_id de la sesion
@app.route("/listmessages", methods=["POST"])
def listmessages():
    return jsonify({**{"message": messagedict[chatlist[session["chat_id"]-1]]}, **{"chat_id": session["chat_id"]}})
