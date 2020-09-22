from typing import Union, Callable, List, Optional

import gui_main
from gui_main import GUIMain
import threading
import soundcard as sc
import numpy as np
import time

NUMBER_OF_FRAMES = None
SAMPLE_RATE = 48000
BLOCKSIZE = 1024
EXCLUSIVE_MODE = True


class Main:
    """
    The main class.
    """
    input_devices = []
    output_devices = []

    threads: List[List[Optional[threading.Thread]]]
    # gui_thread: threading.Thread

    run_id: int

    def __init__(self):
        self.gui: GUIMain = GUIMain(self.update)
        self.run_id = 0

    def main(self) -> None:
        """
        The main function.
        Returns when the program exits.
        """
        self.gui.main()
        self.run_id = -1

    def get_devices(self) -> None:
        """
        Updates input_devices and output_devices
        """
        self.input_devices = []
        for s in self.gui.win_vars.input_sound:
            if s.name == gui_main.DEFAULT_SOUND_NAME:
                continue
            self.input_devices.append(sc.get_microphone(id=s.name, include_loopback=True))

        self.output_devices = []
        for s in self.gui.win_vars.output_sound:
            if s.name == gui_main.DEFAULT_SOUND_NAME:
                continue
            self.output_devices.append(sc.get_microphone(id=s.name, include_loopback=True))

    def create_threads(self) -> None:
        """
        Creates the audio threads. This is called when Update is pushed.
        """
        self.threads = [[None] * len(self.gui.win_vars.output_sound)] * len(self.gui.win_vars.input_sound)

        for x, i in enumerate(self.gui.win_vars.input_sound):
            for y, o in enumerate(self.gui.win_vars.output_sound):
                if i.name == gui_main.DEFAULT_SOUND_NAME or o.name == gui_main.DEFAULT_SOUND_NAME:
                    continue

                self.threads[x][y] = threading.Thread(target=self.output_thread,
                                                      args=(self.run_id,
                                                            sc.get_microphone(i.name, True), lambda: i.volume,
                                                            sc.get_speaker(o.name), lambda: o.volume))
                self.threads[x][y].start()

    def output_thread(self, my_run_id: int, source,
                      source_volume: Callable[[], float],
                      target, target_volume: Callable[[], float]) -> None:
        """
        The audio thread.
        :param my_run_id: The current run_id.
        :param source: The source Microphone.
        :param source_volume: The source volume.
        :param target: The target Speaker.
        :param target_volume: The target volume.
        """
        with source.recorder(samplerate=SAMPLE_RATE, blocksize=BLOCKSIZE, channels=2) as mic, \
                target.player(samplerate=SAMPLE_RATE, blocksize=BLOCKSIZE) as sp:
            while self.run_id == my_run_id:
                data = mic.record(numframes=NUMBER_OF_FRAMES)
                sp.play(data * source_volume() / 100 * target_volume() / 100)

    def update(self) -> None:
        """
        Updates the threads to reflect changes. Called when Update is pushed.
        """
        self.run_id += 1
        time.sleep(1)
        self.create_threads()
        print("Updated.")


if __name__ == '__main__':
    Main().main()
