from flask import Flask, request, render_template
import requests

app = Flask(__name__)

FB_API_URL = "https://graph.facebook.com/v17.0"

# ✅ Fetch Group Chats with Names & Photo
def get_group_chats(access_token):
    url = f"{FB_API_URL}/me/groups?fields=id,name,icon&access_token={access_token}"
    response = requests.get(url)
    data = response.json()

    gc_list = []
    if "data" in data:
        for chat in data["data"]:
            gc_name = chat.get("name", f"Unnamed ({chat['id']})")
            gc_photo = chat.get("icon", "https://via.placeholder.com/50")
            gc_list.append({"id": chat["id"], "name": gc_name, "photo": gc_photo})
    return gc_list

# ✅ Fetch Messages with User Info & Profile Pics
def get_chat_messages(gc_id, access_token):
    url = f"{FB_API_URL}/{gc_id}/feed?fields=from,message,created_time,full_picture&access_token={access_token}"
    response = requests.get(url)
    data = response.json()

    messages = []
    if "data" in data:
        for msg in data["data"]:
            user_id = msg["from"]["id"]
            user_name = msg["from"]["name"]
            profile_pic = f"https://graph.facebook.com/{user_id}/picture?type=normal"
            messages.append({
                "user_id": user_id,
                "name": user_name,
                "profile_pic": profile_pic,
                "message": msg.get("message", "[Media]"),
                "time": msg["created_time"]
            })
    return messages

@app.route("/", methods=["GET", "POST"])
def home():
    gc_list = []
    access_token = ""

    if request.method == "POST":
        access_token = request.form.get("access_token")
        gc_list = get_group_chats(access_token)

    return render_template("home.html", gc_list=gc_list, access_token=access_token)

@app.route("/chat/<gc_id>")
def chat(gc_id):
    access_token = request.args.get("access_token")
    messages = get_chat_messages(gc_id, access_token)

    # Fetch GC Name & Photo
    gc_info = next((gc for gc in get_group_chats(access_token) if gc["id"] == gc_id), {})
    return render_template("chat.html", messages=messages, gc_info=gc_info)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
