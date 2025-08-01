from machine import Pin, PWM
import time
import math

class MotorController:
    """Simple DC motor controller using PWM and direction pins"""
    
    def __init__(self, pwm_pin, dir_pin1, dir_pin2, freq=1000):
        self.pwm = PWM(Pin(pwm_pin))
        self.pwm.freq(freq)
        self.dir1 = Pin(dir_pin1, Pin.OUT)
        self.dir2 = Pin(dir_pin2, Pin.OUT)
        self.stop()
    
    def forward(self, speed):
        """Move motor forward with given speed (0-100)"""
        self.dir1.value(1)
        self.dir2.value(0)
        duty = int((speed / 100) * 65535)
        self.pwm.duty_u16(duty)
    
    def backward(self, speed):
        """Move motor backward with given speed (0-100)"""
        self.dir1.value(0)
        self.dir2.value(1)
        duty = int((speed / 100) * 65535)
        self.pwm.duty_u16(duty)
    
    def stop(self):
        """Stop the motor"""
        self.dir1.value(0)
        self.dir2.value(0)
        self.pwm.duty_u16(0)
    
    def brake(self):
        """Brake the motor (short both terminals)"""
        self.dir1.value(1)
        self.dir2.value(1)
        self.pwm.duty_u16(65535)

class ServoController:
    """Servo motor controller using PWM"""
    
    def __init__(self, pin, freq=50, min_us=544, max_us=2400):
        self.pwm = PWM(Pin(pin))
        self.pwm.freq(freq)
        self.min_us = min_us
        self.max_us = max_us
        self.set_angle(90)  # Center position
    
    def set_angle(self, angle):
        """Set servo angle (0-180 degrees)"""
        angle = max(0, min(180, angle))
        pulse_us = self.min_us + (angle / 180) * (self.max_us - self.min_us)
        duty = int((pulse_us / 20000) * 65535)  # 20ms period
        self.pwm.duty_u16(duty)
    
    def set_microseconds(self, us):
        """Set servo position directly in microseconds"""
        us = max(self.min_us, min(self.max_us, us))
        duty = int((us / 20000) * 65535)
        self.pwm.duty_u16(duty)

class StepperController:
    """Simple stepper motor controller (4-wire)"""
    
    def __init__(self, pin1, pin2, pin3, pin4, delay_ms=2):
        self.pins = [Pin(pin1, Pin.OUT), Pin(pin2, Pin.OUT), 
                     Pin(pin3, Pin.OUT), Pin(pin4, Pin.OUT)]
        self.delay_ms = delay_ms
        self.position = 0
        
        # Step sequence for full step mode
        self.sequence = [
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ]
    
    def step(self, direction=1):
        """Perform one step (direction: 1=forward, -1=backward)"""
        step_index = self.position % len(self.sequence)
        
        for i, pin in enumerate(self.pins):
            pin.value(self.sequence[step_index][i])
        
        self.position += direction
        time.sleep_ms(self.delay_ms)
    
    def rotate(self, steps, direction=1):
        """Rotate by specified number of steps"""
        for _ in range(abs(steps)):
            self.step(direction if steps > 0 else -direction)
    
    def stop(self):
        """Stop and disable all coils"""
        for pin in self.pins:
            pin.value(0)

def main():
    """Main motor control example"""
    print("Motor Control Example")
    print("=" * 25)
    
    # Initialize motors
    dc_motor = MotorController(pwm_pin=2, dir_pin1=3, dir_pin2=4)
    servo = ServoController(pin=5)
    stepper = StepperController(pin1=6, pin2=7, pin3=8, pin4=9)
    
    print("Testing DC Motor...")
    # Test DC motor
    for speed in [30, 60, 100]:
        print(f"Forward at {speed}% speed")
        dc_motor.forward(speed)
        time.sleep(2)
    
    dc_motor.stop()
    time.sleep(1)
    
    for speed in [30, 60, 100]:
        print(f"Backward at {speed}% speed")
        dc_motor.backward(speed)
        time.sleep(2)
    
    dc_motor.stop()
    print("DC motor test complete")
    
    print("\nTesting Servo Motor...")
    # Test servo motor
    angles = [0, 45, 90, 135, 180, 90]
    for angle in angles:
        print(f"Moving to {angle} degrees")
        servo.set_angle(angle)
        time.sleep(1)
    
    print("Servo test complete")
    
    print("\nTesting Stepper Motor...")
    # Test stepper motor
    print("Rotating 200 steps forward")
    stepper.rotate(200, direction=1)
    time.sleep(1)
    
    print("Rotating 200 steps backward")
    stepper.rotate(200, direction=-1)
    stepper.stop()
    
    print("Motor control test complete")

def smooth_servo_sweep():
    """Smooth servo sweep demonstration"""
    print("Smooth Servo Sweep Demo")
    servo = ServoController(pin=5)
    
    try:
        while True:
            # Smooth sweep using sine wave
            for i in range(360):
                angle = 90 + 45 * math.sin(math.radians(i * 2))
                servo.set_angle(angle)
                time.sleep_ms(20)
    except KeyboardInterrupt:
        servo.set_angle(90)  # Return to center
        print("\nServo sweep stopped")

if __name__ == "__main__":
    main()
    # Uncomment for smooth servo demo:
    # smooth_servo_sweep()
