import PySimpleGUI as sg
import soundcard as sc
from typing import List, Callable, Any

TITLE = 'SoundClone'
DEFAULT_SOUND_NAME = 'None'
VOLUME_RANGE = (0, 125)
DEFAULT_VOLUME = 100


class GUIMain:
    """
    The GUI class.
    """
    win_vars: 'WindowVars'
    window: sg.Window

    def __init__(self, on_update: Callable[[], Any]):
        """

        :param on_update: A callable that will be called when 'Update' is pushed.
        """
        self.on_update = on_update
        self.win_vars: 'WindowVars' = WindowVars(input_sound=[SoundVars()])

    def main(self) -> None:
        """
        The main loop. returns when the window quits.
        """
        # sg.theme('DarkAmber')	# Add a touch of color
        # All the stuff inside your window.
        layout = self.get_layout()

        # Create the Window
        self.window = sg.Window(TITLE, layout)
        # Event Loop to process "events" and get the "values" of the inputs
        while True:
            event, values = self.window.read()
            if event == sg.WIN_CLOSED:  # if user closes window
                break

            if 'INPUT_SLIDER' in event:
                self.slider_handler(True, self.get_id(event), values[event])
            if 'OUTPUT_SLIDER' in event:
                self.slider_handler(False, self.get_id(event), values[event])

            if 'INPUT_REMOVE' in event:
                self.remove_handler(True, self.get_id(event))
            if 'OUTPUT_REMOVE' in event:
                self.remove_handler(False, self.get_id(event))

            if 'INPUT_DROPDOWN' in event:
                self.dropdown_handler(True, self.get_id(event), values[event])
            if 'OUTPUT_DROPDOWN' in event:
                self.dropdown_handler(False, self.get_id(event), values[event])

            if event == '-INPUT_ADD-':
                self.add_input()
            if event == '-OUTPUT_ADD-':
                self.add_output()

            if event == '-UPDATE-':
                self.on_update()

        self.window.close()

    def slider_handler(self, is_input: bool, index: int, value: float) -> None:
        """
        Handles changes in sliders.
        :param is_input: is this an input slider?
        :param index: the index of the slider.
        :param value: the new value of the slider.
        """
        (self.win_vars.input_sound if is_input else self.win_vars.output_sound)[index].volume = value

    def remove_handler(self, is_input, index: int) -> None:
        """
        Handles the 'remove' buttons.
        :param is_input: is this an input button?
        :param index: the index of the button.
        """
        if is_input:
            self.remove_input(index)
        else:
            self.remove_output(index)

    def dropdown_handler(self, is_input: bool, index: int, value: str) -> None:
        """
        Handles changes in the dropdowns.
        :param is_input: is this an input dropdown?
        :param index: the index of the dropdown.
        :param value: the new value of the dropdown.
        """
        (self.win_vars.input_sound if is_input else self.win_vars.output_sound)[index].name = value

    @staticmethod
    def get_id(s: str) -> int:
        """
        Extracts the id from an event name.
        :param s: The event.
        :return: The id of the event.
        """
        return int(s[s.index('#') + 1:-1])

    def get_layout(self) -> List[List[Any]]:
        """
        ReCreates the layout.
        :return: The new layout.
        """
        inputs = []
        for i, s in enumerate(self.win_vars.input_sound):
            # noinspection PyTypeChecker
            inputs += [[sg.Text(F'Input {i}:'),
                        sg.DropDown(self.get_microphones(), key=F'-INPUT_DROPDOWN_#{i}-',
                                    default_value=s.name, readonly=True,
                                    enable_events=True)],
                       [sg.Text('Volume:'),
                        sg.Slider(range=VOLUME_RANGE, default_value=s.volume, key=F'-INPUT_SLIDER_#{i}-',
                                  orientation='horizontal', enable_events=True),
                        sg.Button('Remove', key=F'-INPUT_REMOVE_#{i}-')]]

        outputs = []

        for i, s in enumerate(self.win_vars.output_sound):
            # noinspection PyTypeChecker
            outputs += [[sg.Text(F'Output {i}:'),
                         sg.DropDown(self.get_speakers(), key=F'-OUTPUT_DROPDOWN_#{i}-',
                                     default_value=s.name, readonly=True,
                                     enable_events=True)],
                        [sg.Text('Volume:'),
                         sg.Slider(range=VOLUME_RANGE, default_value=s.volume, key=F'-OUTPUT_SLIDER_#{i}-',
                                   orientation='horizontal', enable_events=True),
                         sg.Button('Remove', key=F'-OUTPUT_REMOVE_#{i}-')]]

        # noinspection PyTypeChecker
        layout = inputs + [[sg.Button("Add Input", key='-INPUT_ADD-')]] \
                 + outputs + [[sg.Button("Add Output", key='-OUTPUT_ADD-')],
                              [sg.Button("Update", key="-UPDATE-")]]

        return layout

    def add_input(self) -> None:
        """
        Adds a new input.
        """
        self.win_vars.input_sound.append(SoundVars())
        self.reload_window()

    def remove_input(self, index: int) -> None:
        """
        Removes an input.
        :param index: The index of the input to remove.
        """
        self.win_vars.input_sound.pop(index)
        self.reload_window()

    def add_output(self) -> None:
        """
        Adds a new output.
        """
        self.win_vars.output_sound.append(SoundVars())
        self.reload_window()

    def remove_output(self, index: int) -> None:
        """
        Removes an output.
        :param index: The index of the output to remove.
        """
        self.win_vars.output_sound.pop(index)
        self.reload_window()

    @staticmethod
    def get_microphones() -> List[str]:
        """
        :return: All microphone names, including loopbacks, plus DEFAULT_SOUND_NAME.
        """
        l = [DEFAULT_SOUND_NAME]
        for m in sc.all_microphones(include_loopback=True):
            l.append(m.name)
        return l

    @staticmethod
    def get_speakers() -> List[str]:
        """
        :return: All speaker names, plus DEFAULT_SOUND_NAME.
        """
        l = [DEFAULT_SOUND_NAME]
        for m in sc.all_speakers():
            l.append(m.name)
        return l

    def reload_window(self) -> None:
        """
        Reloads the window with a new layout from get_layout.
        """
        location = self.window.current_location()
        window1 = sg.Window(TITLE, location=location).Layout(self.get_layout())
        self.window.close()
        self.window = window1


class WindowVars:
    """
    Stores all the variable for the window.
    """

    def __init__(self, input_sound: List['SoundVars'] = None,
                 output_sound: List['SoundVars'] = None):
        """

        :param input_sound: The list of all Microphones in use (inputs).
        :param output_sound: The list of all speakers in use (outputs).
        """
        self.output_sound = [] if output_sound is None else output_sound
        self.input_sound = [] if input_sound is None else input_sound

    input_sound: List['SoundVars']

    output_sound: List['SoundVars']


class SoundVars:
    """
    Stores the variables for a Microphone or Speaker.
    """

    def __init__(self, volume: float = DEFAULT_VOLUME, name: str = DEFAULT_SOUND_NAME) -> None:
        """

        :param volume: The volume multiplier, in percent.
        :param name: The name of the Microphone / Speaker.
        """
        self.volume = volume
        self.name = name

    volume: float
    name: str
