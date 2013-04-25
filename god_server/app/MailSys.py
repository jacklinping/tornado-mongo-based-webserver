#-*- encoding: utf-8 -*-
import os,os.path,sys,time,types
import string
import subprocess

class Storage(dict):
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError, k:
            raise AttributeError, k

    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, key):
        try:
            del self[key]
        except KeyError, k:
            raise AttributeError, k

    def __repr__(self):
        return '<Storagee ' + dict.__repr__(self) + '>'

storage = Storage

def dictadd(dict_a, dict_b):
    result = {}
    result.update(dict_a)
    result.update(dict_b)
    return result

def safestr(obj, encoding='utf-8'):
    if isinstance(obj, unicode):
        return obj.encode(encoding)
    elif isinstance(obj, str):
        return obj
    elif hasattr(obj, 'next'):
        return itertools.imap(safestr, obj)
    else:
        return str(obj)


def sendmail(from_address, to_address, subject, message, headers=None, **kw):
    attachments = kw.pop("attachments", [])
    mail = _EmailMessage(from_address, to_address, subject, message, headers, **kw)

    for a in attachments:
        if isinstance(a, dict):
            mail.attach(a['filename'], a['content'], a.get('content_type'))
        elif hasattr(a, 'read'): #file
            filename = os.path.basename(getattr(a, "name", ""))
            content_type = getattr(a, 'content_type', None)
            mail.attach(filename, a.read(), content_type)
        elif isinstance(a, basestring):
            f = open(a, 'rb')
            content = f.read()
            f.close()
            filename = os.path.basename(a)
        else:
            raise ValueError, "Invalid attachment: %s" % repr(a)

    mail.send()


class _EmailMessage:
    def __init__(self, from_address, to_address, subject, message, headers=None, **kw):
        def listify(x):
            if not isinstance(x, list):
                return [safestr(x)]
            else:
                return [safestr(a) for a in x]

        subject = safestr(subject)
        message = safestr(message)

        from_address = safestr(from_address)
        to_address = listify(to_address)
        cc = listify(kw.get('cc', []))
        bcc = listify(kw.get('bcc', []))
        recipients = to_address + cc + bcc

        import email.Utils
        self.from_address = email.Utils.parseaddr(from_address)[1]
        self.recipients = [email.Utils.parseaddr(r)[1] for r in recipients]

        self.headers = dictadd({
            'From': from_address,
            'To': ",".join(to_address),
            'Subject': subject
            }, headers or {})

        if cc:
            self.headers['Cc'] = ",".join(cc)

        self.message = self.new_message()
        self.message.add_header("Content-Transfer-Encoding", "7bit")
        self.message.add_header("Content-Disposition", "inline")
        self.message.add_header("MIME-Version", "1.0")
        self.message.set_payload(message, 'utf-8')
        self.multipart = False

    def new_message(self):
        from email.Message import Message
        return Message()

    def attach(self,filename, content, content_type=None):
        if not self.multipart:
            msg = self.new_message()
            msg.add_header("Content-Type", "multipart/mixeed")
            msg.attach(self.message)
            self.message = msg
            self.multipart = True

        import mimetypes
        try:
            from email import encoders
        except:
            from email import Encoders as encoders

        content_type = content_type or mimetypes.guess_type(filename)[0] or "application/octet-stream"

        msg = self.new_message()
        msg.set_payload(content)
        msg.add_header('Content-Type', content_type)
        msg.add_header('Content-Dispositon', 'attachment', filename=filename)

        if not content_type.startswith("text/"):
            encoders.encode_base64(msg)

        self.message.attach(msg)

    def prepare_message(self):
        for k, v in self.headers.iteritems():
            if k.lower() == "content-type":
                self.message.set_type(v)
            else:
                self.message.add_header(k,v)

        self.headers = {}

    def send(self):
        config = storage()

        self.prepare_message()
        message_text = self.message.as_string()

        if config.get('smtp_server'):
            server = config.get('smtp_server')
            port = config.get('smtp_port', 0)
            username = config.get('smtp_username')
            password = config.get('smtp_password')
            debug_level = config.get('smtp_debuglevel', None)
            starttls = config.get('smtp_starttls', False)

            import smtplib
            smtpserver = smtplib.SMTP(server, port)

            if debug_level:
                smtpserver.set_debuglevel(debug_level)

            if starttls:
                smtpserver.ehlo()
                smtpserver.starttls()
                smtpserver.ehlo()

            if username and password:
                smtpserver.login(username, password)

            smtpserver.sendmail(self.from_address, self.recipients, message_text)
            smtpserver.quit()
        else:
            sendmail = config.get('sendmail_path', '/usr/sbin/sendmail')

#            assert not self.from_address.startwith('-'), 'security'
            for r in self.recipients:
                assert not r.startswith('-'), 'security'

            cmd = [sendmail, '-f', self.from_address] + self.recipients
            print cmd
            if subprocess:
                p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
                p.stdin.write(message_text)
                p.stdin.close()
            else:
                i, o = os.popen2(cmd)
                i.write(message)
                i.close()
                o.close()
                del i, o

    def __repr__(self):
        return "<EmailMessage>"

    def __str__(self):
        return self.message.as_string()

if __name__ == "__main__":
    sendmail('androidesk@androidesk.com',
            'yangmaosheng96@163.com',
            '工作计划',
            '明天晚要开会的，apple'
            )

