import cmd
import json
import paho.mqtt.client as MqttClient
import random
import threading
import time

class Consumer(cmd.Cmd):
    def __init__(self, args, ss_code, ht_code, lt_code):
        self.ss_code = ss_code
        self.ht_code = ht_code
        self.lt_code = lt_code
        self.code = args['code']
        self.prompt = 'powergrid > substation({ss_code}) > ht_line({ht_code}) > lt_line({lt_code}) > consumer({cs_code}) > '.format(ss_code=self.ss_code, ht_code=self.ht_code, lt_code=self.lt_code, cs_code=self.code)
        self.name = args['name']
        self.max_load = args['max_load']
        self.load_type = args['load_type']
        self.voltage_range = 15.0
        self.neutral_range = 5.0
        self.frequency_range = 5.0
        self.load_range = 5.0
        self.phase_a_delta = 0.0
        self.phase_b_delta = 0.0
        self.phase_c_delta = 0.0
        self.neutral_delta = 0.0
        self.frequency_delta = 0.0
        self.load_factor = 0.80
        self.load_delta = 0.0
        self.mqtt_client = MqttClient.Client('{cs_code}'.format(cs_code=self.code))
        self.mqtt_client.username_pw_set('admin', 'hivemq')
        self.mqtt_client.connect('127.0.0.1', 1883)
        self.mqtt_client.loop_start()
        self.thread = threading.Thread(target=self.start_client)
        self.running = True
        self.thread.start()
    
    def start_client(self):
        while(self.running):
            self.mqtt_client.publish('{ss_code}/{ht_code}/{lt_code}/{cs_code}'.format(ss_code=self.ss_code, ht_code=self.ht_code, lt_code=self.lt_code, cs_code=self.code), 
                '''consumer,substation={ss_code},htline={lt_code},ltline={lt_code},cs_code={cs_code} phase_a_voltage={phase_a_voltage},phase_b_voltage={phase_b_voltage},phase_c_voltage={phase_c_voltage},neutral_voltage={neutral_voltage},frequency={frequency},load={load}'''.format(
                    phase_a_voltage = 220 + self.phase_a_delta + random.uniform(-1*self.voltage_range, self.voltage_range),
                    phase_b_voltage = 220 + self.phase_b_delta + random.uniform(-1*self.voltage_range, self.voltage_range),
                    phase_c_voltage = 220 + self.phase_c_delta + random.uniform(-1*self.voltage_range, self.voltage_range),
                    neutral_voltage = self.neutral_delta + random.uniform(-1*self.neutral_range, self.neutral_range),
                    frequency = 50.0 + self.frequency_delta + random.uniform(-1*self.frequency_range, self.frequency_range),
                    load = (self.max_load * self.load_factor) + self.load_delta + random.uniform(-1* self.load_range, self.load_range),
                    ss_code=self.ss_code, ht_code=self.ht_code, lt_code=self.lt_code, cs_code=self.code))
            time.sleep(5)

    def stop_client(self):
        print('Stopping Consumer {ss_code}/{ht_code}/{lt_code}/{cs_code}...'.format(ss_code=self.ss_code, ht_code=self.ht_code, lt_code=self.lt_code, cs_code=self.code))
        self.running = False
        self.thread.join(1)

    def do_exit(self, line):
        """Go back to previous menu"""
        return True


class LTLine(cmd.Cmd):
    def __init__(self, args, ss_code, ht_code):
        super().__init__()
        self.ss_code = ss_code
        self.ht_code = ht_code
        self.code = args['code']
        self.prompt = 'powergrid > substation({ss_code}) > ht_line({ht_code}) > lt_line({lt_code}) > '.format(ss_code=self.ss_code, ht_code=self.ht_code, lt_code=self.code)
        self.name = args['name']
        self.max_load = args['max_load']
        self.voltage_range = 15.0
        self.neutral_range = 5.0
        self.frequency_range = 5.0
        self.load_range = 5.0
        self.phase_a_delta = 0.0
        self.phase_b_delta = 0.0
        self.phase_c_delta = 0.0
        self.neutral_delta = 0.0
        self.frequency_delta = 0.0
        self.load_factor = 0.80
        self.load_delta = 0.0
        self.mqtt_client = MqttClient.Client('{lt_code}'.format(lt_code=self.code))
        self.mqtt_client.username_pw_set('admin', 'hivemq')
        self.mqtt_client.connect('127.0.0.1', 1883)
        self.mqtt_client.loop_start()
        self.thread = threading.Thread(target=self.start_client)
        self.running = True
        self.thread.start()
        self.consumers = {}
        if 'consumers' in args:
            for cs in args['consumers']:
                consumer = Consumer(cs, self.ss_code, self.ht_code, self.code)
                self.consumers[cs['code']] = consumer

    def start_client(self):
        while(self.running):
            self.mqtt_client.publish('{ss_code}/{ht_code}/{lt_code}'.format(ss_code=self.ss_code, ht_code=self.ht_code, lt_code=self.code), 
                '''ltline,substation={ss_code},htline={ht_code},ltline={lt_code} phase_a_voltage={phase_a_voltage},phase_b_voltage={phase_b_voltage},phase_c_voltage={phase_c_voltage},frequency={frequency},load={load}'''.format(
                    phase_a_voltage = 220 + self.phase_a_delta + random.uniform(-1*self.voltage_range, self.voltage_range),
                    phase_b_voltage = 220 + self.phase_b_delta + random.uniform(-1*self.voltage_range, self.voltage_range),
                    phase_c_voltage = 220 + self.phase_c_delta + random.uniform(-1*self.voltage_range, self.voltage_range),
                    neutral_voltage = self.neutral_delta + random.uniform(-1*self.neutral_range, self.neutral_range),
                    frequency = 50.0 + self.frequency_delta + random.uniform(-1*self.frequency_range, self.frequency_range),
                    load = (self.max_load * self.load_factor) + self.load_delta + random.uniform(-1* self.load_range, self.load_range),
                    ss_code=self.ss_code, ht_code=self.ht_code, lt_code=self.code))
            time.sleep(5)

    def stop_client(self):
        print('Stopping LTLine {ss_code}/{ht_code}/{lt_code}...'.format(ss_code=self.ss_code, ht_code=self.ht_code, lt_code=self.code))
        self.running = False
        self.thread.join(1)
        for consumer in self.consumers:
            self.consumers[consumer].stop_client()

    def do_show(self, line):
        """Show list of Consumers"""
        for consumer in self.consumers:
                print(consumer)

    def do_list(self, line):
        """Show List of available parameters"""
        print("1. voltage_range")
        print("2. neutral_range")
        print("3. frequency_range")
        print("4. load_range")
        print("5. phase_a_delta")
        print("6. phase_b_delta")
        print("7. phase_c_delta")
        print("8. neutral_delta")
        print("9. frequency_delta")
        print("10. load_factor")
        print("11. load_delta")

    def do_set(self, line):
        """Set LTLine Simulation Parameters (set parameter_name value)"""
        args = line.split()
        if(hasattr(self, args[0])):
            setattr(self, args[0], float(args[1]))
        else:
            print("Error: Invalid Parameter")

    def do_exit(self, line):
        """Go back to previous menu"""
        return True

class HTLine(cmd.Cmd):
    def __init__(self, args, ss_code):
        super().__init__()
        self.ss_code = ss_code
        self.code = args['code']
        self.prompt = 'powergrid > substation({ss_code}) > ht_line({ht_code}) > '.format(ss_code=self.ss_code, ht_code=self.code)
        self.name = args['name']
        self.max_load = args['max_load']
        self.voltage_range = 200.0
        self.frequency_range = 5.0
        self.load_range = 10.0
        self.phase_a_delta = 0.0
        self.phase_b_delta = 0.0
        self.phase_c_delta = 0.0
        self.frequency_delta = 0.0
        self.load_factor = 0.80
        self.load_delta = 0.0
        self.mqtt_client = MqttClient.Client('{ht_code}'.format(ht_code=self.code))
        self.mqtt_client.username_pw_set('admin', 'hivemq')
        self.mqtt_client.connect('127.0.0.1', 1883)
        self.mqtt_client.loop_start()
        self.thread = threading.Thread(target=self.start_client)
        self.running = True
        self.thread.start()
        self.ltLines = {}
        if 'lt_lines' in args:
            for lt in args['lt_lines']:
                ltLine = LTLine(lt, self.ss_code, self.code)
                self.ltLines[lt['code']] = ltLine

    def start_client(self):
        while(self.running):
            self.mqtt_client.publish('{ss_code}/{ht_code}'.format(ss_code=self.ss_code, ht_code=self.code), 
                '''htline,substation={ss_code},htline={ht_code} phase_a_voltage={phase_a_voltage},phase_b_voltage={phase_b_voltage},phase_c_voltage={phase_c_voltage},frequency={frequency},load={load}'''.format(
                    phase_a_voltage = 11000 + self.phase_a_delta + random.uniform(-1*self.voltage_range, self.voltage_range),
                    phase_b_voltage = 11000 + self.phase_b_delta + random.uniform(-1*self.voltage_range, self.voltage_range),
                    phase_c_voltage = 11000 + self.phase_c_delta + random.uniform(-1*self.voltage_range, self.voltage_range),
                    frequency = 50.0 + self.frequency_delta + random.uniform(-1*self.frequency_range, self.frequency_range),
                    load = (self.max_load * self.load_factor) + self.load_delta + random.uniform(-1* self.load_range, self.load_range),
                    ss_code=self.ss_code, ht_code=self.code))
            time.sleep(5)

    def do_show(self, line):
        """Show list of LTLines"""
        for ltLine in self.ltLines:
                print(ltLine)

    def do_list(self, line):
        """Show List of available parameters"""
        print("1. voltage_range")
        print("2. frequency_range")
        print("3. load_range")
        print("4. phase_a_delta")
        print("5. phase_b_delta")
        print("6. phase_c_delta")
        print("7. frequency_delta")
        print("8. load_factor")
        print("9. load_delta")


    def do_set(self, line):
        """Set HTLine Simulation Parameters (set parameter_name value)"""
        args = line.split()
        if(hasattr(self, args[0])):
            setattr(self, args[0], float(args[1]))
        else:
            print("Error: Invalid Parameter")

    def do_use(self, lt_code):
        """Select LTLine"""
        if lt_code in self.ltLines:
            self.ltLines[lt_code].cmdloop()
        else:
            print("Error: Unknown LTLine Code")

    def do_exit(self, line):
        """Go back to previous menu"""
        return True

    def stop_client(self):
        print('Stopping HTLine {ss_code}/{ht_code}...'.format(ss_code=self.ss_code, ht_code=self.code))
        self.running = False
        self.thread.join(1)
        for ltLine in self.ltLines:
            self.ltLines[ltLine].stop_client()


class SubStation(cmd.Cmd):
    def __init__(self, args):
        super().__init__()
        self.code = args['code']
        self.prompt = 'powergrid > substation({ss_code}) > '.format(ss_code=self.code)
        self.name = args['name']
        self.max_load = args['max_load']
        self.voltage_range = 300.0
        self.frequency_range = 5.0
        self.load_range = 20.0
        self.phase_a_delta = 0.0
        self.phase_b_delta = 0.0
        self.phase_c_delta = 0.0
        self.frequency_delta = 0.0
        self.load_factor = 0.80
        self.load_delta = 0.0
        self.mqtt_client = MqttClient.Client(self.code)
        self.mqtt_client.username_pw_set('admin', 'hivemq')
        self.mqtt_client.connect('127.0.0.1', 1883)
        self.mqtt_client.loop_start()
        self.thread = threading.Thread(target=self.start_client)
        self.running = True
        self.thread.start()
        self.htLines = {}
        if 'ht_lines' in args:
            for ht in args['ht_lines']:
                htLine = HTLine(ht, self.code)
                self.htLines[ht['code']] = htLine

    def start_client(self):
        while(self.running):
            self.mqtt_client.publish('{ss_code}'.format(ss_code=self.code), 
                '''substation,substation={ss_code} phase_a_voltage={phase_a_voltage},phase_b_voltage={phase_b_voltage},phase_c_voltage={phase_c_voltage},frequency={frequency},load={load}'''.format(
                    phase_a_voltage = 33000 + self.phase_a_delta + random.uniform(-1*self.voltage_range, self.voltage_range),
                    phase_b_voltage = 33000 + self.phase_b_delta + random.uniform(-1*self.voltage_range, self.voltage_range),
                    phase_c_voltage = 33000 + self.phase_c_delta + random.uniform(-1*self.voltage_range, self.voltage_range),
                    frequency = 50.0 + self.frequency_delta + random.uniform(-1*self.frequency_range, self.frequency_range),
                    load = (self.max_load * self.load_factor) + self.load_delta + random.uniform(-1* self.load_range, self.load_range),
                    ss_code=self.code))
            time.sleep(5)

    def stop_client(self):
        print('Stopping Substation {ss_code}...'.format(ss_code=self.code))
        self.running = False
        self.thread.join(1)
        for htLine in self.htLines:
            self.htLines[htLine].stop_client()

    def do_show(self, line):
        """Show list of HTLines"""
        for htLine in self.htLines:
                print(htLine)

    def do_list(self, line):
        """Show List of available parameters"""
        print("1. voltage_range")
        print("2. frequency_range")
        print("3. load_range")
        print("4. phase_a_delta")
        print("5. phase_b_delta")
        print("6. phase_c_delta")
        print("7. frequency_delta")
        print("8. load_factor")
        print("9. load_delta")


    def do_set(self, line):
        """Set Substation Simulation Parameters (set parameter_name value)"""
        args = line.split()
        if(hasattr(self, args[0])):
            setattr(self, args[0], float(args[1]))
        else:
            print("Error: Invalid Parameter")

    def do_use(self, ht_code):
        """Select HTLine"""
        if ht_code in self.htLines:
            self.htLines[ht_code].cmdloop()
        else:
            print("Error: Unknown HTLine Code")

    def do_exit(self, line):
        """Go back to previous menu"""
        return True


class PowerGrid(cmd.Cmd):
    """PowerGrid Simulator Console"""
    prompt = 'powergrid > '
    def __init__(self):
        super().__init__()
        with open('infrastructure.json') as infrastructureFile:
            self.infrastructure = json.load(infrastructureFile)
            self.subStations = {}
            for ss in self.infrastructure['substations']:
                subStation = SubStation(ss)
                self.subStations[ss['code']] = subStation

    def do_show(self, line):
        """Show list of substations"""
        for subStation in self.subStations:
                print(subStation)

    def do_use(self, ss_code):
        """Select Substation"""
        if ss_code in self.subStations:
            self.subStations[ss_code].cmdloop()
        else:
            print("Error: Unknown SubStation Code")

    def do_exit(self, line):
        """Shutdown PowerGrid Simulator"""
        for subStation in self.subStations:
            self.subStations[subStation].stop_client()
        return True

    def do_EOF(self, line):
        """Shutdown PowerGrid Simulator"""
        for subStation in self.subStations:
            self.subStations[subStation].stop_client()
        return True


if __name__ == '__main__':
    PowerGrid().cmdloop()

        