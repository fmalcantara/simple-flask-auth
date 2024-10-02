from flask import Flask, request, jsonify
from models.user import User
from database import db
from flask_login import LoginManager, login_user, current_user, logout_user, login_required

app = Flask(__name__)
app.config['SECRET_KEY'] = "your_secret_key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

login_manager = LoginManager()
db.init_app(app)
login_manager.init_app(app)

#view login
login_manager.login_view = 'login'

# session <- conexão ativa
@login_manager.user_loader
def load_user(user_id):
  return User.query.get(user_id)


#rota de Login
@app.route("/login", methods=['POST'])
def login():
  data = request.json
  username = data.get('username')
  password = data.get('password')
  
  if username and password:
    #login
    user = User.query.filter_by(username=username).first()
    
    if user and user.password == password:
      login_user(user)
      print(current_user.is_authenticated)
      return jsonify({"message": f"Usuario {user.username} logado com sucesso!!"}), 200
  return jsonify({"message": "Credenciais invalidas"}), 400


#Rota de Logout
@app.route("/logout", methods=['GET'])
@login_required
def logout():
  logout_user()
  return jsonify({"message": "Logout de realizado com sucesso!!"})


#Rota para Cadastro de usuario geral sem está logado
@app.route('/user', methods=['POST'])
def create_user():
  data = request.json
  username = data.get('username')
  password = data.get('password')
  
  if username and password:
    user = User(username=username, password=password)
    db.session.add(user)
    db.session.commit()
    return jsonify({"message":"Usuario cadastrado com sucesso"})
  
  return jsonify({'message': 'Credenciais invalidas para cadastro de usuario'}), 400


#Rota para buscar um usuario no banco por ID:
@app.route('/user/<int:id_user>', methods=['GET'])
@login_required
def read_user(id_user):
  user = User.query.get(id_user)
  print(user)
  if user:
    return {"username": user.username}
  
  return jsonify({"message":"Usuario não encontrado"})


# Rota para Update
@app.route('/user/<int:id_user>', methods=['PUT'])
@login_required
def update_user(id_user):
  data = request.json
  user = User.query.get(id_user)
  
  if user and data.get("password"):
     user.password = data.get("password")
     db.session.commit()
  
     return jsonify({"message": f"Usuario {id_user} atualizado com sucesso"})
  
  elif not data.get("password"):
    return jsonify({"message": "Senha nao pode ficar branco. Por favor, preencha uma senha"})
  
  return jsonify({"message":"Usuario nao encontrado"}), 404 


# Rota para Delete
@app.route('/user/<int:id_user>', methods=['DELETE'])
@login_required
def delete_user(id_user):
  user = User.query.get(id_user)

  if id_user == current_user.id:
    return jsonify({"message": "Delecao nao permitida para o proprio usuario"}), 403

  if user:
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": f"Usuario {id_user} deletado com sucesso!!"})
  
  return jsonify({"message":"Usuario não encontrado"}), 404

# Rota de teste hello Word
@app.route("/hello-word", methods=["GET"])
def hello_word():
  return "Heloo Woord!"
  
if __name__ == "__main__":
  app.run(debug=True)