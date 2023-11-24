import EF30B

DS1 = EF30B.DigitSelect(2)
DS2 = EF30B.DigitSelect(3)
DS3 = EF30B.DigitSelect(4)

segments = EF30B.SegmentController(EF30B.Segment(13),EF30B.Segment(14),EF30B.Segment(15),EF30B.Segment(16),SEF30B.egment(17),EF30B.Segment(18),EF30B.Segment(19))

leds = [Led(n) for n in [13,14,15,16,17,18,19]]
disp = EF30B.MultipleDigitDisplay(segments, DS1, DS2)

disp.on()
for i in range(1,50):
    disp.value(i)
    time.sleep(0.1)
disp.off()
