#!/usr/bin/env python3
import logging
import os
import re

from gi.repository import Gst
from lib.config import Config
from lib.sources.avsource import AVSource

from vocto.video_codecs import construct_video_decoder_pipeline


class RTMPAVSource(AVSource):
    timer_resolution = 0.5

    def __init__(self, name, has_audio=True, has_video=True, force_num_streams=None):
        self.location = Config.getLocation(name)

        super().__init__(
            "RTMPAVSource", name, has_audio, has_video, show_no_signal=True
        )
        self.build_pipeline()

    def __str__(self):
        return "RTMPAVSource[{name}] displaying {location}".format(
            name=self.name, location=self.location
        )

    def port(self):
        return os.path.basename(self.location)

    def num_connections(self):
        return 1

    def video_channels(self):
        return 1

    def build_source(self):
        source = """
              rtmpsrc
                location={location}
                do-timestamp=TRUE
              ! flvdemux""".format(
            location=self.location
        )
        source += """
                name=rtmp-{name}
            """.format(
            name=self.name
        )

        return source

    def build_videoport(self):
        decoder = construct_video_decoder_pipeline(self.section())
        return """
              rtmp-{name}.
            ! h264parse
            ! {decoder}
            ! videoconvert
            ! videorate
            ! videoscale
            """.format(
            name=self.name, decoder=decoder
        )

    def build_audioport(self):
        return """
              rtmp-{name}.
            ! aacparse
            ! avdec_aac
            ! audioconvert
            ! audioresample
            """.format(
            name=self.name
        )
