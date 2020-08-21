import re


class Tablet:

    def __init__(self, agent):
        self.agent = agent
        self.dialog = None
        self.extras_type = None
        self.extras = ''
        self.extras_params = None

    def get_body(self, dialog=None, extras_type=None, extras_params=None):

        if dialog is not None:
            self.dialog = re.sub(r"\\[a-z]*=[a-z]*[0-9]*\\", '', dialog)

        if extras_type is not None:
            self.extras_type = extras_type

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
        disclaimer = ' <h2 style="color: #009900;">Disclaimer</h2> '
        disclaimer += re.sub(r"\\[a-z]*=[a-z]*[0-9]*\\", '', self.agent.get_sentence('general', 'disclaimer_content'))

        return disclaimer

    def get_employee(self):

        name = self.extras_params[0][0]
        location = self.extras_params[0][2]
        title = self.extras_params[0][3]
        email = self.extras_params[0][4]
        telefone = self.extras_params[0][5]
        group = self.extras_params[0][6]

        employee = ' <h2 style="color: #009900;">Employee info</h2> '
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

        joke = ' <h2 style="color: #009900;">Human-made joke</h2> '
        joke += re.sub(r"\\[a-z]*=[a-z]*[0-9]*\\", '', self.extras_params[1])
        if self.extras_params[0] == 'laugh':
            joke += '</br> <img src="img/laugh1.png" style="width: 180px; height: 180px;">'

        return joke

    def get_poetry(self):

        poetry = ' <h2 style="color: #009900;">My freestyle</h2> '
        for verse in self.extras_params[1]:
            poetry += verse + '</br>'

        if self.extras_params[0] == 'think':
            poetry += '</br> <img src="img/think.png" style="width: 100px; height: 80px;">'

        return poetry

    def reset_extras(self):
        self.extras = ''
        self.extras_type = None

    def get_dialog_div(self):
        # 'padding: 8px 12px; background-image: url(img/ballon.png");>' \
        div = '<div style="width: 90%; height: 10%; font-size: 2vw;' \
                  'border: 1px solid #333; box-shadow: 8px 8px 5px #444;' \
                  'padding: 8px 12px;'\
                  ' background-image: linear-gradient(180deg, #fff, #ddd 40%, #ccc)">' \
                  ' {} ' \
              '</div> </br>'.format(self.dialog)
        return div

    def get_content(self):
        if self.extras_type == 'disclaimer':
            self.extras = self.get_disclaimer()
        if self.extras_type == 'employee':
            self.extras = self.get_employee()
        if self.extras_type == 'joke':
            self.extras = self.get_joke()
        if self.extras_type == 'poetry':
            self.extras = self.get_poetry()

        content = ''
        if self.extras != '':
            content = '<div style="width: 90%; height: 10%; font-color: green; font-size: 2.5vw;' \
                          'border: 1px solid #090; box-shadow: 8px 8px 5px #0c0;' \
                          'padding: 8px 12px; background-image: linear-gradient(180deg, #fff, #ddd 40%, #ccc)">' \
                          ' {} ' \
                      '</div>'.format(self.extras)

        return self.get_dialog_div() + content

    def update_dialog(self, text):
        self.dialog = text


