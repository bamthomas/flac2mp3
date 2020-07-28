#!/usr/bin/env python

import sys
import re
import eyed3
from eyed3.core import Tag
from eyed3.id3.frames import TextFrame, Frame

tag = Tag()


class TextFrameWithUtf8Encoding(Frame):
  def __init__(self, textFrame):
    Frame.__init__(self, textFrame.header, textFrame.unsync_default);
    self.textFrame = textFrame;

  def render(self):
    if self.textFrame.header.minorVersion == 4 and self.textFrame.header.id == "TSIZ":
      TRACE_MSG("Dropping deprecated frame TSIZ")
      return ""
    data = UTF_8_ENCODING + self.textFrame.text.encode(id3EncodingToString(self.textFrame.encoding));
    return self.textFrame.assembleFrame(data);

if len(sys.argv) != 2:
  print("usage : " + sys.argv[0] + " <mp3_file>")
  sys.exit(1)

tag.link(sys.argv[1])

for i in range(0, len(tag.frames)):
  frame=tag.frames[i]
  if frame.__class__ == TextFrame:
    tag.frames[i] = TextFrameWithUtf8Encoding(frame)

tag.update()
