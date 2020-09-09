import re


class Tablet:

    def __init__(self, agent):
        self.agent = agent
        self.dialog = None
        self.extras_type = None
        self.you_chose = None
        self.buttons = []
        self.extras = ''
        self.extras_params = None

    def get_body(self, dialog=None, you_chose=None, buttons=[], extras_type=None, extras_params=None):

        # previous dialog remains until there is a new dialog, but other divs get removed when switching topics
        if dialog is not None:
            self.dialog = re.sub(r"\\[a-z]*=[a-z]*[0-9]*\\", '', dialog)

        if you_chose is not None:
            self.you_chose = you_chose
        else:
            self.you_chose = None

        if extras_type is not None:
            self.extras_type = extras_type

        if len(buttons) > 0:
            self.buttons = buttons

        if extras_params is not None:
            self.extras_params = extras_params

        body = self.get_header_html() + self.get_content() + self.get_footer_html()
        return body

    def get_header_html(self):
        header = '<nav class="navbar mb-5">' \
               '<div class="navbar-brand listening_icon"></div>' \
               '<div class="navbar-nav vu_logo"></div>' \
               '</nav>' \
               '<main class="container text-center">'
        return header

    def get_footer_html(self):
        footer = '</main>' \
                '<footer class="fixed-bottom">' \
                '<p class="lead bg-light text-center speech_text"></p>' \
                '</footer>'
        return footer

    def get_disclaimer(self):
        disclaimer = ' <h3 style="color: #009900;">Disclaimer</h1> '
        disclaimer += re.sub(r"\\[a-z]*=[a-z]*[0-9]*\\", '', self.agent.get_sentence('general', 'disclaimer_content'))

        return disclaimer

    def get_buttons(self):

        div = ''
        if len(self.buttons) > 0:
            div = '<div style="width: 90%; height: 10%; font-size: 2vw;' \
                  'border: 1px solid #333; padding: 8px 12px;">'

            for button in self.buttons:
                div += '<button class="btn btn-primary btn-sm mt-2 ml-2">{}</button>'.format(button)

            div += '<button class="btn btn-warning btn-sm mt-2 ml-2">Leave me alone!</button>'  \
                   '</div> </br>'
        return div

    def get_employee(self):

        name = self.extras_params[0][0]
        location = self.extras_params[0][2]
        title = self.extras_params[0][3]
        email = self.extras_params[0][4]
        telefone = self.extras_params[0][5]
        group = self.extras_params[0][6]

        employee = ' <h3 style="color: #009900;">Employee info</h1> '
        if name is not None:
            employee += ' <b>Name</b>: ' + name

        if title is not None:
            employee += '  </br> <b>Title</b>: ' + title

        if group is not None:
            employee += '  </br> <b>Group</b>: ' + group

        if location is not None:
            employee += ' </br> <b>Location</b>: ' + location

        if email is not None:
            employee += ' </br> <b>E-mail</b>: ' + email

        if telefone is not None:
            employee += ' </br> <b>Telephone</b>: ' + telefone

        return employee

    def get_joke(self):

        joke = ' <h3 style="color: #009900;">Human-made joke</H1> '
        joke += re.sub(r"\\[a-z]*=[a-z]*[0-9]*\\", '', self.extras_params[1])
        if self.extras_params[0] == 'laugh':
            joke += '</br> <img src="img/laugh1.png" style="width: 140px; height: 140px;">'

        return joke

    def get_poetry(self):

        poetry = ' <h3 style="color: #009900;">My freestyle</h1> '
        for verse in self.extras_params[1]:
            poetry += verse + '</br>'

        if self.extras_params[0] == 'think':
            poetry += '</br> <img src="img/think.png" style="width: 60px; height: 40px;">'

        return poetry

    def get_dialog_div(self):
        div = ''
        if self.dialog != '':
            div = '<div style="width: 90%; height: 10%; font-size: 2vw;' \
                      'border: 1px solid #333; box-shadow: 8px 8px 5px #444;' \
                      'padding: 8px 12px;'\
                      ' background-image: linear-gradient(180deg, #fff, #ddd 40%, #ccc)">' \
                      ' <b>Kiko:</b> {} ' \
                  '</div> </br>'.format(self.dialog)
        return div

    def get_yousaid_div(self):
        div = ''
        if self.you_chose is not None and self.you_chose != '':
            div = '<div style="width: 90%; height: 10%; font-size: 2vw;' \
                      'border: 1px solid #333; box-shadow: 8px 8px 5px #444;' \
                      'padding: 8px 12px;'\
                      ' background-image: linear-gradient(180deg, #fff, #ddd 40%, #ccc)">' \
                      ' <b>You chose:</b> {} ' \
                  '</div> </br>'.format(self.you_chose)
        return div

    def get_extras(self):

        if self.extras_type == 'disclaimer':
            self.extras = self.get_disclaimer()
        if self.extras_type == 'employee':
            self.extras = self.get_employee()
        if self.extras_type == 'joke':
            self.extras = self.get_joke()
        if self.extras_type == 'poetry':
            self.extras = self.get_poetry()
        if self.extras_type == '':
            self.extras = ''

        div = ''
        if self.extras != '':
            div = '<div style="width: 90%; height: 10%; font-color: green; font-size: 2vw;' \
                          'border: 1px solid #090; box-shadow: 8px 8px 5px #0c0;' \
                          'padding: 8px 12px; background-image: linear-gradient(180deg, #fff, #ddd 40%, #ccc)">' \
                          ' {} ' \
                      '</div>'.format(self.extras)
        return div

    def get_content(self):
        return self.get_dialog_div() + self.get_buttons() + self.get_yousaid_div() + self.get_extras()

    def resets_screen(self):
        self.dialog = ''
        self.you_chose = ''
        self.buttons = []
        self.extras_type = ''
        return self.get_body()

    def reset_extras(self):
        self.extras_type = None
        self.extras = ''


