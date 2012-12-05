from ctypes import *

wand = cdll.LoadLibrary(r'C:\Program Files\ImageMagick-6.8.0-Q16\CORE_RL_wand_.dll')
wand.MagickWandGenesis()
wand.MagickGetImageBlob.restype = POINTER(c_ubyte)

def resize(max_width, max_height, data):
	b = None
	m_wand = wand.NewMagickWand()
	if wand.MagickReadImageBlob(m_wand, data, len(data)):
		width = wand.MagickGetImageWidth(m_wand)
		height = wand.MagickGetImageHeight(m_wand)

		if width > height:
			r = max_width/width
		else:
			r = max_height/height

		w = int(r * width)
		h = int(r * height)

		wand.MagickResizeImage(m_wand, w, h, 1, 1)
		wand.MagickSetImageCompressionQuality(m_wand, 95)
		size = pointer(c_size_t())
		wand.MagickSetImageFormat(m_wand, b'jpg')
		wand_buf = wand.MagickGetImageBlob(m_wand, size)
		b = bytes([wand_buf[i] for i in range(size.contents.value)])
		wand.MagickRelinquishMemory(wand_buf)

	wand.DestroyMagickWand(m_wand)
	return b

def end():
	wand.MagickWandTerminus()

