from flask import Flask, render_template, request, redirect
import database

app = Flask(__name__)

# Initialize database
database.init_db()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/homestay")
def homestay():
    return render_template("homestay.html")


@app.route("/healthcare")
def healthcare():
    return render_template("healthcare.html")


@app.route("/admin")
def admin():
    homestays = database.get_homestays()
    healthcare = database.get_healthcare()

    return render_template(
        "admin.html",
        homestays=homestays,
        healthcare=healthcare
    )


@app.route("/register-homestay", methods=["POST"])
def register_homestay():

    data = (
        request.form["property_name"],
        request.form["owner_name"],
        request.form["mobile"],
        request.form["address"],
        request.form["location"],
        int(request.form["rooms"]),
        int(request.form["beds"]),
        float(request.form["price"]),
        request.form["facilities"]
    )

    database.add_homestay(data)

    return redirect("/admin")


@app.route("/register-healthcare", methods=["POST"])
def register_healthcare():

    data = (
        request.form["booth_name"],
        request.form["organization"],
        request.form["location"],
        request.form["doctor"],
        request.form["services"],
        request.form["hours"],
        int(request.form["beds"] or 0),
        request.form["oxygen"],
        request.form["ambulance"]
    )

    database.add_healthcare(data)

    return redirect("/admin")


@app.route("/verify-homestay/<int:id>")
def verify_homestay(id):

    database.verify_homestay(id)

    return redirect("/admin")


@app.route("/verify-healthcare/<int:id>")
def verify_healthcare(id):

    database.verify_healthcare(id)

    return redirect("/admin")


if __name__ == "__main__":
    app.run(debug=True)