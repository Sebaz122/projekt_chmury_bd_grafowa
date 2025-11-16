from flask import Flask, jsonify, render_template, request
import os
from pyvis.network import Network
from neo4j import GraphDatabase
from flask_cors import CORS  
from dotenv import load_dotenv


app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)

load_dotenv()
NEO4J_URI=os.environ.get("NEO4J_URI")
NEO4J_USER=os.environ.get("NEO4J_USER")
NEO4J_PASSWORD=os.environ.get("NEO4J_PASSWORD")
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

@app.route("/api/users", methods=["GET"])
def get_users():
    with driver.session() as session:
        result = session.run("MATCH (u:User) RETURN u")
        users = [record["u"] for record in result]
        return jsonify([dict(u) for u in users])


@app.route("/api/users", methods=["POST"])
def add_user():
    data = request.json
    name = data.get("name")
    if not name:
        return jsonify({"error": "Missing 'name'"}), 400
    
    with driver.session() as session:
        is_in_base = session.run("MATCH (u:User {name: $name}) RETURN u",name=name).single()
        if (is_in_base):
            return jsonify({"error": "user_already_exists"}), 409
        session.run("CREATE (u:User {name: $name})", name=name)

    return jsonify({"status": "user_created", "name": name})

@app.route("/api/interests", methods=["GET"])
def get_interests():
    with driver.session() as session:
        result = session.run("MATCH (i:Interest) RETURN i")
        interests = [dict(record["i"]) for record in result]
        return jsonify(interests)

@app.route("/api/interests", methods=["POST"])
def add_interest():
    data = request.json
    name = data.get("name")

    if not name:
        return jsonify({"error": "Missing 'name'"}), 400

    with driver.session() as session:
        is_in_base = session.run("MATCH (i:Interest {name: $name}) RETURN i",name=name).single()
        if(is_in_base):
            return jsonify({"error": "interest_already_exists"}), 409
        
        session.run("CREATE (i:Interest {name: $name})", name=name)

    return jsonify({"status": "interest_created", "name": name})

@app.route("/api/friends", methods=["POST"])
def add_friendship():
    data = request.json
    user_a = data.get("from")
    user_b = data.get("to")
    if not user_a or not user_b:
        return jsonify({"error": "Missing 'from' or 'to' field"}), 400
    
    with driver.session() as session:
        is_user_a = session.run("MATCH (u:User {name: $user_a}) RETURN u", user_a=user_a).single()
        is_user_b = session.run("MATCH (u:User {name: $user_b}) RETURN u", user_b=user_b).single()
        if not is_user_a:
            return jsonify({"error": "user_a_not_found"}), 404
        if not is_user_b:
            return jsonify({"error": "user_b_not_found"}), 404
        existing = session.run("""MATCH (:User {name: $user_a})-[r:FRIENDS_WITH]-(:User {name: $user_b})RETURN r LIMIT 1""", user_a=user_a, user_b=user_b).single()
        if existing:
            return jsonify({"error": "friendship_already_exists"}), 409
        session.run("""MATCH (u1:User {name: $user_a}), (u2:User {name: $user_b}) MERGE (u1)-[:FRIENDS_WITH]->(u2)""",user_a=user_a, user_b=user_b)

    return jsonify({"status": "is_friends_with", "from": user_a, "to": user_b})

@app.route("/api/likes", methods=["POST"])
def add_likes():
    data = request.json
    user = data.get("user")
    interest = data.get("interest")

    if not user:
        return jsonify({"error": "Missing 'user'"}), 400

    with driver.session() as session:
        is_user = session.run("MATCH (u:User {name: $name}) RETURN u", name = user).single()
        if not is_user:
            return jsonify({"error": "no_user_found"}), 404
        existing = session.run("""MATCH (:User {name: $name})-[l:LIKES]-(i:Interest {name: $interest}) RETURN l LIMIT 1""", name=user, interest=interest).single()
        if existing:
            return jsonify({"error": "user_already_likes"}), 409
        
        session.run("""MATCH (u:User {name: $name}), (i:Interest {name: $interest}) MERGE (u)-[:LIKES]->(i) """, name=user, interest=interest)

    return jsonify({"status": "likes_created", "user": user, "interest": interest})

@app.route("/api/delete_user", methods = ["POST"])
def delete_user():
    data = request.json
    user = data.get("user")

    if not user:
        return jsonify({"error": "no_user_provided"}), 400
    
    with driver.session() as session:
        is_user = session.run("MATCH (u:User {name: $name}) RETURN u" , name=user).single()
        if not is_user:
            return jsonify({"error": "no_user_found"}), 404
        session.run("MATCH (u:User {name: $name}) DETACH DELETE u", name = user)
        return jsonify({"status": "user_deleted", "user": user})

@app.route("/api/delete_interest", methods=["POST"])
def delete_interest():
    data = request.json
    interest = data.get("interest")

    if not interest:
        return jsonify({"error": "no_interest"}), 400
    
    with driver.session() as session:
        is_interest = session.run("MATCH (i:Interest {name: $interest}) RETURN i", interest=interest).single()
        if not is_interest:
            return jsonify({"error":"no_interest_found"}), 404
        session.run("MATCH (i:Interest {name: $interest}) DETACH DELETE i", interest=interest)
        return jsonify({"status":"interest_deleted", "interest": interest})
  
@app.route("/api/delete_friendship", methods=["POST"])
def delete_friendship():
    data = request.json
    user_a = data.get("user_a")
    user_b = data.get("user_b")
    if not user_a:
        return jsonify({"error": "no_user_a"}), 400
    if not user_b:
        return jsonify({"error": "no_user_b"}), 400
    
    with driver.session() as session:
        result  = session.run("MATCH (a:User {name: $user_a})-[f:FRIENDS_WITH]->(b:User {name: $user_b}) RETURN a,f,b", user_a=user_a, user_b=user_b).single()
        if result is None:
            return jsonify({"error":"incorrect_users_or_friendship_already_deleted"}), 409
        
        session.run("MATCH (a:User {name: $user_a})-[f:FRIENDS_WITH]->(b:User {name: $user_b}) DELETE f", user_a=user_a, user_b=user_b)
        return jsonify({"status":"friendship_deleted", "user_a": user_a, "user_b": user_b})
    
@app.route("/api/delete_likes", methods=["POST"])
def delete_likes():
    data = request.json
    user = data.get("user")
    interest = data.get("interest")
    if not user:
        return jsonify({"error": "no_user"}), 400
    if not interest:
        return jsonify({"error": "no_interest"}), 400
    
    with driver.session() as session:
        result  = session.run("MATCH (u:User {name: $name})-[l:LIKES]->(i:Interest {name: $interest}) RETURN u,l,i", name=user, interest=interest).single()
        if result is None:
            return jsonify({"error":"incorrect_user_interest_or_likes_already_deleted"}), 409
    
        session.run("MATCH (u:User {name: $name})-[l:LIKES]->(i:Interest {name: $interest}) DELETE l", name=user, interest=interest)
        return jsonify({"status":"likes_deleted", "user": user, "interest": interest})

@app.route("/api/change_username", methods =["POST"])
def change_username():
    data = request.json
    old_username = data.get("old_username")
    new_username = data.get("new_username")
    if not old_username:
        return jsonify({"error": "no_old_username"}), 400
    if not new_username:
        return jsonify({"error": "no_new_username"}), 400
    
    with driver.session() as session:
        is_old_user = session.run("MATCH (ou:User {name: $old_username}) RETURN ou", old_username=old_username).single()
        is_new_user = session.run("MATCH (nu:User {name: $new_username}) RETURN nu", new_username=new_username).single()
        if is_new_user:
            return jsonify({"error":"new_username_already_taken", "old_username": old_username, "new_username": new_username}), 409
        if not is_old_user:
            return jsonify({"error":"username_does_not_exist", "old_username": old_username}), 404
        session.run("MATCH (ou:User {name:$old_username}) SET ou.name = $new_username", old_username=old_username, new_username=new_username)
        return jsonify({"status":"username_changed", "old_username": old_username, "new_username": new_username})

@app.route("/api/add_user_information", methods=["POST"])
def add_user_information():
    data=request.json
    info_key = data.get("info_key")
    info_value = data.get("info_value")
    user= data.get("user")
    if not info_key:
        return jsonify({"error": "no_information_key"}), 400
    if not info_value:
        return jsonify({"error": "no_information_value"}), 400
    if not user:
        return jsonify({"error": "no_user"}), 400
    
    with driver.session() as session:
        is_user = session.run("MATCH (u:User {name: $name}) RETURN u" , name=user).single()
        if not is_user:
            return jsonify({"error": "no_user_found"}), 404
        session.run("MATCH (u:User {name:$name}) SET u[$info_key] = $info_value", name=user, info_key=info_key, info_value=info_value)
        return jsonify({"status": "user_information_added", "user": user, "info_key": info_key, "info_value": info_value})
    
@app.route("/api/find_user_friends", methods=["POST"])
def find_user_friends():
    data=request.json
    user=data.get("user")
    if not user:
        return jsonify({"error": "no_user"}), 400
    with driver.session() as session:
        is_user = session.run("MATCH (u:User {name: $name}) RETURN u" , name=user).single()
        if not is_user:
            return jsonify({"error": "no_user_found"}), 404
        user_friends_all = session.run("MATCH (u:User {name: $name})-[f:FRIENDS_WITH]->(uf:User) RETURN uf", name=user)
        friends = [user_friends["uf"] for user_friends in user_friends_all]
        return jsonify([dict(uf) for uf in friends])
    
@app.route("/api/find_user_interests", methods=["POST"])
def find_user_interests():
    data=request.json
    user=data.get("user")
    if not user:
        return jsonify({"error": "no_user"}), 400
    with driver.session() as session:
        is_user = session.run("MATCH (u:User {name: $name}) RETURN u" , name=user).single()
        if not is_user:
            return jsonify({"error": "no_user_found"}), 404
        user_interests_all = session.run("MATCH (u:User {name: $name})-[l:LIKES]->(i:Interest) RETURN i", name=user)
        user_interests = [user_interests["i"] for user_interests in user_interests_all]
        return jsonify([dict(i) for i in user_interests])
    
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/uzytkownik")
def view_users():
    return render_template("users.html")

@app.route("/zainteresowanie")
def view_interests():
    return render_template("interests.html")

@app.route("/relacje")
def view_relations():
    return render_template("relations.html")

@app.route("/graph")
def graph():
    net = Network(height="720px", width="100%", directed=True, bgcolor="#ffffff")
    net.show_buttons(filter_=["physics"])

    with driver.session() as session:
        for record in session.run("MATCH (u:User) RETURN u.name AS name"):
            name = record["name"]
            net.add_node(f"U:{name}", label=name, group="User", shape="dot", color="#1f77b4")
        for record in session.run("MATCH (i:Interest) RETURN i.name AS name"):
            name = record["name"]
            net.add_node(f"I:{name}", label=name, group="Interest", shape="box", color="#ff7f0e")
        for record in session.run("MATCH (a:User)-[:FRIENDS_WITH]->(b:User) RETURN a.name AS a, b.name AS b"):
            net.add_edge(f"U:{record['a']}", f"U:{record['b']}", color="#4c78a8", title="FRIENDS_WITH")
        for record in session.run("MATCH (u:User)-[:LIKES]->(i:Interest) RETURN u.name AS u, i.name AS i"):
            net.add_edge(f"U:{record['u']}", f"I:{record['i']}", color="#f58518", title="LIKES")
    out_path = os.path.join(app.root_path, "templates", "graph.html")
    net.write_html(out_path)
    return render_template("graph.html")

if __name__ == "__main__":
    #do zmiany przed deploymentem na false
    app.run()