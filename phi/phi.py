#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, render_template, session, abort, request, g
from flask import redirect, url_for, flash, make_response, jsonify, send_file

from PIL import Image, ImageDraw, ImageFont
from StringIO import StringIO

import re

app = Flask(__name__)
app.debug = True

if app.debug:
    from werkzeug import SharedDataMiddleware
    import os
    app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
      '/': os.path.join(os.path.dirname(__file__), 'static')
    })

@app.route("/")
def index():
	return render_template('index.html')

@app.route("/<int:width>/<int:height>/<mime>/<background>/<text>")
@app.route("/<int:width>/<int:height>/<mime>/<background>")
@app.route("/<int:width>/<int:height>/<mime>")
@app.route("/<int:width>/<int:height>")
@app.route("/<int:width>", defaults={"height": None}) # square images
def image(width, height, background=None, text=None, mime="png"):
	if height is None:
		height = width

	if width > 4000:
		width = 4000
	if height > 4000:
		height = 4000
	if width < 1:
		width = 1
	if height < 1:
		height = 1

	img_args = {
		"width": width,
		"height": height,
		"background": background,
		"text": text
	}
	img = make_pil_image(**img_args)
	return send_pil_image(img, mime=mime)

def valid_hexa(chex, default, reg=r'^\#([a-fA-F0-9]{3}|[a-fA-F0-9]{6})$'):
	if chex is None:
		return default
	if chex[0] is not '#':
		# account for missing hash
		chex = '#{0}'.format(chex)
	if not re.match(reg, chex, flags=re.I):
		return default
	else:
		return chex

def send_pil_image(img, mime="png"):
	mime = mime.lower()
	if mime in ('gif'):
		type_ = "GIF"
		mimetype = "image/gif"
	elif mime in ('jpg', 'jpeg'):
		type_ = "JPEG"
		mimetype = "image/jpg"
	else:
		type_ = "PNG"
		mimetype = "image/png"
	img_io = StringIO()
	img.save(img_io, type_, optimize=True)
	img_io.seek(0)
	return send_file(img_io, mimetype=mime)

def make_pil_image(width=100, height=100, background=None, text=None):
	background = valid_hexa(background, "#EBF2F5")
	if text is not None:
		text = valid_hexa(text, None)

	img = Image.new("RGB", (width, height), background)
	draw = ImageDraw.Draw(img)
	if text is not None: #6F6F6F
		font = ImageFont.truetype("DejaVuSans-Bold.ttf", 16)
		draw.text((5, 5), u"{0}x{1}".format(width, height), text, font=font)
	return img

def main():
	app.run(port=8080)

if __name__ == "__main__":
	main()