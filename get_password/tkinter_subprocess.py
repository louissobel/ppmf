"""
should be invoked as a subprocess,
will print it's received password on stdout

exit 1 if canceled
exit 0 if OK
"""
import sys
from Tkinter import *

CANCEL_RETURN_CODE = 55

class Application(Frame):

    def __init__(self, master, **kwargs):
        Frame.__init__(self, master, padx=100)

        self.forwhat = kwargs['forwhat']
        self.result = None

        self.pack()
        self.createWidgets()


    def got_password(self):
        self.result = self.password.get()
        self.quit()

    def handle_return_event(self, e):
        return self.got_password()

    def createWidgets(self):

        message_text = "Enter Password for file %s" % self.forwhat
        Label(self, text=message_text).grid(row=0, column=0, columnspan=2)

        self.password = Entry(self)
        self.password["show"] = "*"
        self.password.grid(row=1,column=0,columnspan=2)
        self.password.focus()
        self.password.bind("<Return>", self.handle_return_event)

        self.cancel = Button(self)
        self.cancel["text"] = "Cancel",
        self.cancel["command"] = self.quit
        self.cancel.grid(row=2,column=0)

        self.ok = Button(self)
        self.ok["text"] = "Ok"
        self.ok["command"] = self.got_password
        self.ok.grid(row=2, column=1)

if __name__ == "__main__":
    root = Tk()
    root.wm_title('Cryptbox Password Required')
    app = Application(master=root, forwhat=sys.argv[1])

    app.mainloop()

    if app.result is None:
        sys.exit(CANCEL_RETURN_CODE)
    else:
        sys.stdout.write(app.result)
        sys.exit(0)
