import argparse
import os
import shutil
import sys

import uvicorn
from app.main import app_factory


def flush_logs():
    folder = "./app/logs"
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print("Failed to delete %s. Reason: %s" % (file_path, e))


def run(args=sys.argv):
    print("running")
    print(args)


def tests():
    pass


# def server(args=sys.argv):
def server():
    parser = argparse.ArgumentParser()
    # parser.
    parser.add_argument(
        "--dev",
        action="store_true",
        dest="dev",
        default=False,
    )
    args = parser.parse_args()

    if args.dev == "True":
        import inquirer
        from dotenv import load_dotenv

        load_dotenv()
        questions = [
            inquirer.List(
                "postgres",
                message="Which database do you want to use?",
                choices=[
                    "{}:{}".format(k, v)
                    for k, v in os.environ.items()
                    if "POSTGRES" in k
                ],
            ),
            inquirer.List(
                "redis",
                message="Which redis database do you want to use?",
                choices=[
                    "{}:{}".format(k, v) for k, v in os.environ.items() if "REDIS" in k
                ],
            ),
            inquirer.Checkbox(
                "innit",
                message="Enable init processes",
                choices=["logging", "middlewares", "exceptions", "routers", "postgres"],
                default=["middlewares", "exceptions", "routers"],
                ignore=False,
                carousel=True,
            ),
            inquirer.Text("name", message="What's your name"),
            inquirer.Text("surname", message="What's your surname"),
        ]
        answers = inquirer.prompt(questions)
        print(answers)

    print(args)

    app = app_factory(
        logging="logging" in answers["innit"],
        middelewares="middlewares" in answers["innit"],
        exceptions="exceptions" in answers["innit"],
        routers="routers" in answers["innit"],
        postgres="postgres" in answers["innit"],
    )

    uvicorn.run(app=app)
