from datetime import datetime, timedelta
import os
import renpy
import time
import math

demo_status = {
    'current_index': -1, 'args': {},
    'last_snapshot': None, 'schedule': [],
    }

orig_plog = renpy.plog
def plog_override(*args, **kwargs):
    # Target specific renpy.plog execution in renpy/execution.py
    may_update = len(args) == 2 and args[0] == 1 and args[1].startswith('start of interact while loop')
    after_start(may_update)
    global orig_plog
    orig_plog(*args, **kwargs)
renpy.plog = plog_override

def after_start(is_update_frame):
    if not getattr(renpy.store, 'devtoolsDemoReady', False):
        return
    if is_update_frame:
        schedule_handler()
    snapshot_handler()

snapshot_queue = []
def snapshot_handler():
    global demo_status
    current_time = datetime.now()
    if demo_status['last_snapshot'] is None:
        demo_status['last_snapshot'] = datetime.now() + timedelta(seconds = demo_status['args'].render_delay - 1/demo_status['args'].render_fps)
    interval = timedelta(seconds = 1/demo_status['args'].render_fps)
    delta = current_time - demo_status['last_snapshot']
    if demo_status['args'].render and delta > interval:
        demo_status['last_snapshot'] += math.floor(delta/interval) * interval
        outfile = os.path.join(demo_status['args'].destination, current_time.strftime(demo_status['args'].filename))
        dimensions = demo_status['args'].render_size if demo_status['args'].render_size else (renpy.store.config.screen_width, renpy.store.config.screen_height)
        renpy.game.interface.take_screenshot(dimensions)
        global snapshot_queue
        snapshot_queue.append((outfile, renpy.game.interface.get_screenshot()))

def snapshot_writer():
    global snapshot_queue
    id = 0
    while True:
        time.sleep(1)
        while len(snapshot_queue) > 0:
            snap = snapshot_queue.pop(0)
            id += 1
            with open(snap[0].format(id), 'wb') as f:
                f.write(snap[1])

def schedule_handler():
    global demo_status
    time = datetime.now().timestamp()

    if demo_status['current_index'] == -1:
        demo_status['current_index'] = 0
        demo_status['schedule'][0].load(demo_status, time)
    current = demo_status['schedule'][demo_status['current_index']]
    if current.is_up(demo_status, time):
        current.on_up(demo_status, time)
    else:
        demo_status['current_index'] += 1
        if demo_status['current_index'] < len(demo_status['schedule']):
            demo_status['schedule'][demo_status['current_index']].load(demo_status, time)
        e = None
        try:
            current.on_end(demo_status, time)
        except Exception as e:
            raise e
        if e is None:
            schedule_handler()

def inject_start_label(args):
    pad = '    '
    s = ''
    s += 'default devtoolsDemoReady = False\n'
    s += 'label main_menu_screen:\n'
    s += pad + "$ preferences.afm_enable = True\n"
    s += pad + "$ preferences.afm_time = {}\n".format(args.afm_time)
    for p in args.exec:
        s += pad + "{}\n".format(p)
    if args.commands:
        s += pad + "$ devtoolsDemoReady = True\n"
        s += pad + '""\n'
        s += pad + 'window hide\n'
        s += pad + 'window auto\n'
        s += pad + 'while True:\n'
        s += pad*2 + 'pause 0.01\n'
    else:
        s += pad + '"No command was provided, add one with --label"\n'
        s += pad + '$ renpy.quit()\n'

    fn = "/dev/devtools/demotools_start_label.rpy"
    renpy.game.script.load_string(fn, s)

class ScheduleItem:
    def __init__(self, kind, value = None, delay = None):
        self.kind = kind
        self.value = value
        self.delay = delay
        self.time = 0

    def load(self, context, time):
        self.time = time

    def is_up(self, context, st):
        if self.delay:
            return self.delay + self.time > st
        else:
            return False

    def on_end(self, context, st):
        pass

    def on_up(self, context, st):
        pass

class CursorScheduleItem(ScheduleItem):
    def on_end(self, context, st):
        renpy.store.renpy.set_mouse_pos(*self.value)

class UIScheduleItem(ScheduleItem):
    def is_up(self, context, st):
        if self.delay is None:
            return not len(renpy.store.renpy.get_return_stack()) == 0
        else:
            return super(UIScheduleItem, self).is_up(context, st)

class CallScheduleItem(UIScheduleItem):
    def on_end(self, context, st):
        if self.kind == 'call':
            renpy.store.renpy.call(self.value)()
        elif self.kind == 'show':
            renpy.store.renpy.show_screen(self.value)
        elif self.kind == 'jump':
            renpy.store.renpy.jump(self.value)
        elif self.kind == 'hidescreen':
            renpy.store.renpy.hide_screen(self.value)

class LoopScheduleItem(UIScheduleItem):
    def on_end(self, context, st):
        context['current_index'] = -1

class ExitScheduleItem(UIScheduleItem):
    def on_end(self, context, st):
        renpy.store.renpy.quit()

class PauseScheduleItem(UIScheduleItem):
    pass

def demotools_command():
    ap = renpy.arguments.ArgumentParser()

    ap.add_argument("commands", default=[], nargs='+', action="store", help="The actions to perform.")
    ap.add_argument("--afm-time", default=8, type = float, action="store", help="The afm_time value to use (this will persist after the demo ends)")
    ap.add_argument("--exec", default=[], action="append", help="Python instructions to execute before starting the loop")
    ap.add_argument("--render", default=False, action="store_true", help="Whether to generate a render")
    ap.add_argument("--render-delay", default=0.1, type = float, action="store", help="Initial delay before rendering starts")
    ap.add_argument("--render-size", default=None, action="store", help="Size of the image snapshots taken as a tuple (width, height)")
    ap.add_argument("--render-fps", default=30, type = float, action="store", help="How many frames to generate per second")
    ap.add_argument("--render-format", default="image", action="store", help="How to generate the output (only 'image' is supported at the moment)")
    ap.add_argument("--destination", default=".", action="store", help="Where generated files should be stored")
    ap.add_argument("--filename", default='snapshot-%Y-%m-%d_%H-%M-%S-%f.png', action="store", help="The file name pattern to use for output file")

    args = ap.parse_args()

    # update args for later use and globally save new dict
    global demo_status
    demo_status['args'] = args
    if demo_status['args'].render_size != None:
        render_size = [int(i) for i in demo_status['args'].render_size.split(':')]
        if len(render_size) != 2:
            raise Exception("Invalid render size, needs to be two pixel sizes separated by a column (received: {})".format(demo_status['args'].render_size))
        demo_status['args'].render_size = render_size
    demo_status['schedule'] = []
    for l in args.commands:
        # TODO: Add parameter parsing for duration & modifiers
        arg = l.split('=')
        if len(arg) > 2:
            raise Exception("Improperly formatted parameter: '{}'".format(l))
        arg = (arg[0].strip(), arg[1].strip() if len(arg) > 1 else '')
        if arg[0] in ['call', 'show', 'jump', 'hidescreen']:
            info = [i.strip() for i in arg[1].split(':')]
            item = CallScheduleItem(arg[0], *info)
            # demo_status['schedule'].append({'key': arg[0], 'value': info[0], 'delay': float(info[1]) if len(info) > 1 else None})
        elif arg[0] == 'cursor':
            pos = [float(i) for i in arg[1].split(':')]
            if len(pos) < 2 or len(pos) > 4:
                raise "Invalid cursor parameter, requires two floats separated by ':' ({})".format(l)
            item = CursorScheduleItem('cursor', pos[:3], pos[3] if len(pos) > 3 else None)
        elif arg[0] == 'loop':
            if args.render:
                raise Exception("Using a loop when rendering is not supported")
            item = LoopScheduleItem(arg[0], None, float(arg[1]) if arg[1] else None)
        elif arg[0] == 'quit':
            item = ExitScheduleItem(arg[0], None, float(arg[1]) if arg[1] else None)
        elif arg[0] == 'pause':
            item = PauseScheduleItem(arg[0], None, float(arg[1]) if arg[1] else None)
        else:
            raise Exception("Invalid command key: '{}' (from '{}')".format(arg[0], l))
        demo_status['schedule'].append(item)
    demo_status['schedule'].append(ExitScheduleItem('final_quit', None, None))
    # Inject start and update checkpoints
    if args.render:
        renpy.exports.invoke_in_thread(snapshot_writer)
    inject_start_label(args)

    return True
