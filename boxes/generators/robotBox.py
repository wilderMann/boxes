from boxes import BoolArg, Boxes
import math

class RobotBox(Boxes):
    """Box mit allen aussparungen für einen kleinen Roboter"""

    def __init__(self):
        Boxes.__init__(self)
        # Nur Standardargumente angeben, thickness NICHT explizit
        self.buildArgParser(
            x=100,  # Breite
            y=100,  # Tiefe
            h=60,  # Höhe

        )
        self.argparser.add_argument(
            "--holes_for_cables",
            action="store",  # Checkbox in der UI
            type = BoolArg(),
            default=True,
            help="Löcher für Kabel im Deckel hinzufügen?"
        )
        self.argparser.add_argument(
            "--draw_calliope",
            action="store",  # Checkbox in der UI
            type = BoolArg(),
            default=True,
            help="Soll der Umriss eines Calliope in den Deckel gezeichnet werden?"
        )
        self.argparser.add_argument(
            "--line_sensor",
            action="store",  # Checkbox in der UI
            type=BoolArg(),
            default=False,
            help="[WORK IN PROGRESS] Öffnung für Liniensensor hinzufügen?"
        )
        self.argparser.add_argument(
            "--dist_sensor",
            action="store",  # Checkbox in der UI
            type=BoolArg(),
            default=False,
            help="[WORK IN PROGRESS] Öffnung für Abstandssensor hinzufügen?"
        )

    def render(self):
        edges = "eeee"
        walls = [
            (self.x, self.y, "bottom"),  # Boden
            (self.x, self.y, "top"),  # Deckel
            (self.x, self.h, "front"),  # Vorderseite
            (self.y, self.h, "left"),  # Seite links
            (self.x, self.h, "back"),  # Rückseite
            (self.y, self.h, "right"),  # Seite rechts
        ]
        for w, h, side in walls:
            # Callback-Liste: Nur für die erste Kante die Löcher setzen, Rest None
            def add_corner_holes():
                # Die vier Ecken der Wand, 5mm nach innen versetzt
                positions = [
                    (10.346, 10.346),
                    (w-10.346, 10.346),
                    (w-12.8995, h-12.8995),
                    (12.8995, h-12.8995)
                ]
                if side == "left":
                    add_motor_holes_left()
                if side == "right":
                    add_motor_holes_right()
                if side == "bottom":
                    add_bottom_cutouts()
                if side == "top":
                    add_lid_magnet_mount()
                if (side != "bottom") and (side != "top"):
                    for (cx, cy) in positions:
                        self.circle(cx, cy, 1.5)  # 3mm Durchmesser = 1.5mm Radius



            def add_motor_holes_left():
                # Loch für achse und positions knopf
                self.circle(27.5, 11.15, 3.75)
                self.circle(38.5, 11.15, 2)
                x0, y0 = 30, 22.3
                dx, dy = 20, 4
                self.rectangularHole(x0, y0, dx, dy, 0, False, False)


            def add_motor_holes_right():
                # Loch für achse und positions knopf
                self.circle( w-27.5,11.15, 3.75)
                self.circle( w-38.5,11.15, 2)
                x0, y0 = w-50, 22.3
                dx, dy = 20, 4
                self.rectangularHole(x0, y0, dx, dy, 0, False, False)

            def add_bottom_cutouts():
                # Löcher für die ausschnitte am Boden hinzufügen
                x0, y0 = 19, 55
                dx, dy = 4, 20
                self.rectangularHole(x0, h-y0, dx, dy, 0, False, False)
                self.rectangularHole(w-x0-dx, h-y0, dx, dy, 0, False, False)
                self.circle(w/2, 6, 1.5)
                positions_bottom = [
                    (10.346, 10.346),
                    (w - 10.346, 10.346),
                    (w - 10.346, h - 10.346),
                    (10.346, h - 10.346)
                ]
                for (cx, cy) in positions_bottom:
                    self.circle(cx, cy, 1.5)  # 3mm Durchmesser = 1.5mm Radius


            def add_lid_magnet_mount():
                positions_lid = [
                    (11, 11),
                    (w - 11, 11),
                    (w - 11, h - 11),
                    (11, h - 11)
                ]
                for (cx, cy) in positions_lid:
                    self.circle(cx, cy, 6.5)  # 13mm Durchmesser = 6.5mm Radius
                if self.holes_for_cables:
                    positions_cables = [
                        (w / 2-35, h / 2 + h / 5),
                        (w / 2+35, h / 2 + h / 5),
                        (w / 2 - 35, h / 2 - h / 5),
                        (w / 2+35, h / 2 - h / 5)
                    ]
                    for(cx, cy) in positions_cables:
                        self.rectangularHole(cx, cy, 10, 15,2)
                if self.draw_calliope:
                    distance_middle = start_to_center_offset(points_turtle_calliope)
                    self.moveTo(w/2+distance_middle[0], h/2+distance_middle[1])
                    # Argumentliste für polyline erzeugen
                    args = points_to_boxes_polyline(points_turtle_calliope)
                    self.polyline(*args)


            def start_to_center_offset(points):
                # Mittelpunkt berechnen
                xs = [x for x, y in points]
                ys = [y for x, y in points]
                x_center = (min(xs) + max(xs)) / 2
                y_center = (min(ys) + max(ys)) / 2

                # Startpunkt
                x0, y0 = points[0]

                # Offset berechnen
                dx = x0 - x_center
                dy = y0 - y_center
                return (dx, dy)

            def points_to_boxes_polyline(points):
                # 1. Mittelpunkt der Bounding Box berechnen
                xs = [x for x, y in points]
                ys = [y for x, y in points]
                x_center = (min(xs) + max(xs)) / 2
                y_center = (min(ys) + max(ys)) / 2

                # 2. Alle Punkte um Mittelpunkt verschieben
                centered = [(x - x_center, y - y_center) for x, y in points]

                # 3. Länge und Winkel berechnen (boxes.py erwartet: Länge, relativer Drehwinkel, Länge, ...)
                args = []
                segs = []
                for i in range(1, len(centered)):
                    x0, y0 = centered[i - 1]
                    x1, y1 = centered[i]
                    dx = x1 - x0
                    dy = y1 - y0
                    length = math.hypot(dx, dy)
                    angle = math.degrees(math.atan2(dy, dx))
                    segs.append((length, angle))
                if not segs:
                    return []
                args.append(0)
                args.append(18)
                args.append(segs[0][0])  # Erste Strecke
                prev_angle = segs[0][1]
                for length, angle in segs[1:]:
                    rel_angle = angle - prev_angle
                    # Normiere auf -180..180 Grad
                    while rel_angle <= -180:
                        rel_angle += 360
                    while rel_angle > 180:
                        rel_angle -= 360
                    args.append(rel_angle)
                    args.append(length)
                    prev_angle = angle
                return args

            points_turtle_calliope = [
                (100.85618, 53.086711),
                (102.67409460353109, 53.7005707913705),
                (104.22947667815788, 54.84384177107852),
                (105.83678743188537, 55.91555700057258),
                (107.51654064218657, 56.86974094982238),
                (109.25985410989244, 57.70220274836349),
                (111.05801906119875, 58.40848830667593),
                (112.90184574603353, 58.98521608184173),
                (114.78203994490347, 59.429478707538614),
                (115.38317999999998, 60.8674667899728),
                (115.38317999999998, 62.79990156129318),
                (115.49183777616248, 64.71161970530054),
                (117.287997595179, 65.08867700000003),
                (119.22043236649938, 65.08867700000003),
                (121.15286713781975, 65.08867700000003),
                (123.01784913053663, 64.85002604532086),
                (123.23317999999999, 62.9753968282944),
                (123.23317999999999, 61.04296205697403),
                (123.64244570037907, 59.447441970837076),
                (125.52570246636763, 59.01610572633228),
                (127.3751106480006, 58.45741055812609),
                (129.1818552397664, 57.77334259064816),
                (130.93777885284982, 56.96780830671178),
                (132.634369684486, 56.043861975567815),
                (134.26394766583815, 55.00630551399739),
                (135.8090353758927, 53.849310790283994),
                (137.59685941522272, 53.15310847539046),
                (139.51347040827432, 53.22946281330036),
                (141.2427404478568, 54.05927642097317),
                (142.49683087622998, 55.511169793929405),
                (143.06691635510677, 57.34246289087822),
                (142.92531743466054, 59.26246339314814),
                (142.76837550400748, 61.18818981607274),
                (142.74786374172163, 63.12009887989702),
                (142.86576604661332, 65.04846093973669),
                (143.1195425450219, 66.96365816126163),
                (143.50895882572834, 68.85590054576319),
                (144.0323009591851, 70.71552858959647),
                (144.6867153726051, 72.5331363974983),
                (145.46834297800407, 74.2997724669261),
                (146.4098889678736, 75.985215790401),
                (147.53278414292785, 77.55756222629213),
                (148.76144257721288, 79.04868725660766),
                (150.0887372215988, 80.45265375739359),
                (151.50892611173828, 81.76253399891812),
                (153.01537580525147, 82.97218431581693),
                (154.60115473914146, 84.07573255114826),
                (156.2587068064995, 85.06817403412016),
                (157.98009077727588, 85.94518287160186),
                (159.74836163630795, 86.71703069487056),
                (161.1774675786988, 87.99616334351538),
                (161.9817330665559, 89.73763030541085),
                (162.02255095585468, 91.65571999357017),
                (161.29570584410385, 93.43051082747037),
                (159.92463333678396, 94.77210278073359),
                (158.16790797886534, 95.56849715892692),
                (156.42898226839915, 96.41019061998685),
                (154.75407286713792, 97.37306048569666),
                (153.15164679143828, 98.45235728856991),
                (151.6301575290127, 99.64316608469693),
                (150.19760284235082, 100.93962575386408),
                (148.86213483712615, 102.33584918003143),
                (147.62902106285733, 103.82316547753206),
                (146.5051755759335, 105.39463263034843),
                (145.54889992458922, 107.07142987450246),
                (144.7642987726901, 108.8368955427874),
                (144.10260255862735, 110.65199770584124),
                (143.56568521527734, 112.50788732008523),
                (143.15761828752224, 114.39634798796277),
                (142.87986887569883, 116.30832158195447),
                (142.73314509305578, 118.23482435127981),
                (142.7183907973206, 120.16690897382193),
                (142.8367405145236, 122.09540909157293),
                (143.02462637668393, 124.01314427404773),
                (142.53587888142042, 125.86824153022147),
                (141.34378520416564, 127.3717082570827),
                (139.65292354523933, 128.27678666513265),
                (137.74112773102266, 128.43782316580132),
                (135.92548440808574, 127.8176042831176),
                (134.37131934587526, 126.67236469229961),
                (132.76287030166242, 125.60242874413416),
                (131.08261274508646, 124.64919342399702),
                (129.33867834089426, 123.81818044141968),
                (127.5400083710787, 123.11327995234201),
                (125.6958602018267, 122.5378394601722),
                (123.81531800251733, 122.09535651181258),
                (121.9909924364819, 121.57058013269865),
                (121.11362643153423, 119.8773349498133),
                (119.39886576662538, 119.09974894730836),
                (117.63281412104148, 119.75070156221221),
                (116.7436049205867, 121.43083997345539),
                (114.99324072312774, 122.07926621186802),
                (113.10964068930521, 122.5084092061863),
                (111.25963283342584, 123.06479772234013),
                (109.45234916106783, 123.74726113777974),
                (107.69576928015294, 124.55135043613924),
                (105.99852293114745, 125.47408267628245),
                (104.3680139647139, 126.51021922819268),
                (102.82333407496105, 127.6679341882822),
                (101.03803368624935, 128.3704567602304),
                (99.12126471325881, 128.3024054013082),
                (97.38826955577642, 127.4799987512075),
                (96.12902999271044, 126.03245749719336),
                (95.55126538688242, 124.20364904119762),
                (95.68847172497351, 122.28355972874058),
                (95.84688738434545, 120.35801322281363),
                (95.86869851489054, 118.4261345687941),
                (95.75299703457937, 116.49763618541621),
                (95.4997395322913, 114.58238590792725),
                (95.111783528897, 112.68985442882625),
                (94.58962250908057, 110.82990320979566),
                (93.93656392360829, 109.01181316063406),
                (93.1562124261763, 107.24461512065386),
                (92.21747022479703, 105.55759525812051),
                (91.09480060273596, 103.98510440262041),
                (89.8674567258886, 102.49292576088256),
                (88.54099313461333, 101.0882082742626),
                (87.12154381371188, 99.77756372409854),
                (85.61594585321113, 98.56689578835162),
                (84.03106101577991, 97.46207016455627),
                (82.37452236684133, 96.4679584021496),
                (80.65365299211481, 95.58995376229139),
                (78.88486040382038, 94.81918418754364),
                (77.45050154042238, 93.546106086685),
                (76.63830348995141, 91.8082627692466),
                (76.59088815619485, 89.89020548277432),
                (77.3100070465025, 88.11235730084151),
                (78.67551473987389, 86.76476744713291),
                (80.43101010565069, 85.96567083165571),
                (82.17072981225748, 85.12558298550755),
                (83.84630836609428, 84.16383896630796),
                (85.4493625896715, 83.0854408684599),
                (86.97166660129824, 81.8956470037351),
                (88.40471278514515, 80.59973107517503),
                (89.74171627769492, 79.20498902660813),
                (90.97582054193693, 77.71849321154026),
                (92.10063582239427, 76.14774698376107),
                (93.05933383367548, 74.47230737515734),
                (93.84495133727425, 72.70731057878585),
                (94.50878410984448, 70.8929610456503),
                (95.04632267977627, 69.03723915563961),
                (95.45557878790764, 67.14904689153663),
                (95.7346749728062, 65.23725067810167),
                (95.88274708236642, 63.310829478652856),
                (95.89832551833679, 61.378780710473734),
                (95.7811814286348, 59.45022310399421),
                (95.59053033405347, 57.532501840881885),
                (96.07124062487395, 55.674980088724915),
                (97.25820524165763, 54.16736353249864),
                (98.94501306041812, 53.254753245986414),
                (100.85618, 53.086711)
            ]


            callbacks = [add_corner_holes, None, None, None]
            # queue: bottom top front left back right
            if side == "bottom":
                self.rectangularWall(w, h, edges=edges, callback=callbacks, move="right")
            if side == "top":
                self.rectangularWall(w, h, edges=edges, callback=callbacks, move="up")
            if side == "front":
                self.rectangularWall(w, h, edges=edges, callback=callbacks)
            if side == "left":
                self.rectangularWall(w, h, edges=edges, callback=callbacks, move="left up")
            if side == "back":
                self.rectangularWall(w, h, edges=edges, callback=callbacks, move="right")
            if side == "right":
                self.rectangularWall(w, h, edges=edges, callback=callbacks, move="right up")

        self.moveTo(self.thickness+2,0,-90)
        for _ in range(2):
            self.polyline(10,-90,self.thickness,90,20,90,self.thickness,-90,10,90,10,(90,3),34,(90,3),10,90)
            self.moveTo(self.thickness+40,0)
        for _ in range(2):
            self.polyline(2,-90,self.thickness,90,20,90,self.thickness,-90,2,90,10,(90,3),18,(90,3),10,90)
            self.moveTo(self.thickness+25,0)




