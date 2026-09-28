# A1 — anatomy-inspired hand, wrist and proximal forearm actuation

This revision replaces A0's distributed motors and fixed wrist with a proximal motor cassette, a tapered forearm, paired structural rails and an articulated wrist. This is a CAD prototype and a review package; no physical performance or payload has been established.

## How anatomy informed the design

The [American Society for Surgery of the Hand describes forearm flexor muscles continuing into tendons toward the fingers](https://www.assh.org/handcare/blog/what-is-a-flexor-tendon-injury). A1 uses this separation as its main design principle: actuator mass is near the elbow end; long tendon sheaths carry motion toward the distal forearm and hand. The user's request to put every motor at the proximal end is a packaging choice, rather than a claim that every human forearm muscle belly is located there.

The [radius and ulna are separate forearm structures](https://www.ncbi.nlm.nih.gov/books/NBK544512/). Here they inspire two hollow, slightly curved load-bearing rails. They remain fixed relative to one another. Pronation/supination, which in humans involves radioulnar movement, is not included in A1.

The human wrist permits flexion/extension and radial/ulnar deviation. A1 approximates these motions using a crossed-axis wrist; human wrist motion includes coordinated movement among carpal bones, so this is an engineering simplification, not an anatomically exact joint. See the [experimental wrist kinematics paper by Youm et al.](https://pubmed.ncbi.nlm.nih.gov/670263/) and the [review of wrist anatomy, biomechanics and loads](https://pmc.ncbi.nlm.nih.gov/articles/PMC8880601/).

The palm has a narrower proximal outline, a metacarpal fan, staggered knuckle positions, slight finger splay and a shallow transverse arch. Pinned phalanges, palmar flexor guides and dorsal elastic returns remain serviceable. The thumb has separate opposition and coupled flexion. This design does not recreate human extensor expansion, intrinsic hand muscles or independently controlled finger joints.

## Packaging and actuation

| Feature | A1 CAD |
|---|---|
| Motor placement | Two opposed banks × two levels × two rows, all at the proximal end |
| Motor body locations along forearm | Approximately y = −241 to −160 mm |
| Motor body envelope | 20 × 34 × 26 mm |
| Proximal shell section | 90 × 70 mm |
| Distal shell section | 56 × 36 mm |
| Forearm shell length | 218 mm, from y = −253 to −35 mm |
| Actuated wrist | Flexion/extension and radial/ulnar deviation |
| Initial wrist review limits | −30° extension to +40° flexion; ±20° deviation |
| Moving joints / motor channels | 17 / 8 |
| Tendon spool radius | 8 mm |
| Wrist tendon sector radius | 14 mm |
| Joint hardware | 3 mm finger pins, 5 mm wrist axles, 8 mm OD wrist bushings |
| Forearm skins | Two removable 3 mm wall halves |

M1 index, M2 middle, M3 ring, M4 little, M5 thumb flexion, M6 thumb opposition, M7 wrist flexion/extension and M8 wrist deviation. **Each finger is independently actuated:** any finger can curl while the others remain open. A single finger’s joints share its one tendon and are not independently commanded. The preview includes individual sliders for all five fingers, plus separate thumb opposition and wrist controls. Each wrist motor has two grooves, with one tendon winding while the opposite tendon pays out. Finger opening uses passive elastic returns, as in A0. The wrist uses opposed tendon pairs for bidirectional actuation.

The proximal cassette contains all eight motor bodies within roughly 84 mm along the forearm. Capstans face outward from the two banks. This packs the mechanisms in a short muscle-belly region and leaves the long distal region for lightweight structural rails and tendons. The forearm is slimmer distally rather than uniformly narrow; finite-sized motors still create a proximal bulge.

## Candidate actuator and sizing

The verified packaging reference is [ROBOTIS XC330-M288-T](https://emanual.robotis.com/docs/en/dxl/x/xc330-m288/): 20 × 34 × 26 mm, 23 g, 3.7–6 V, recommended 5 V. It supports current control and current-based position control. Published 0.93 N·m at 5 V is a stall rating; it is not a continuous operating rating.

A1 deliberately changes the actuator reference from A0's larger XL430. **Do not carry A0's 11.1–12 V motor supply into this revision.** Final power, connectors and protection must match the selected 5 V-class actuators. Eight listed 1.80 A stall currents total 14.4 A; this is a transient sizing reference, not normal consumption or a recommendation to stall the motors.

With an 8 mm spool, 20 N tendon tension requires 0.16 N·m ideal motor torque, or 0.24 N·m using a 1.5 sizing factor. The assumed sustainable design torque is 0.25 N·m pending supplier curves and thermal/duty testing. At a 14 mm wrist sector, 20 N tendon tension gives 0.28 N·m ideal wrist torque before friction and opposing-tendon preload. Hand mass and payload at their actual lever arms must be measured before establishing a wrist load rating.

Approximate finger take-up remains 29.45 mm for 75°/90°/60° at 7.5 mm leverage, requiring about 211° of 8 mm spool rotation. Thumb curl takes approximately 17.67 mm / 127° of spool rotation. For 40° wrist motion, a 14 mm sector takes up 9.77 mm and the 8 mm motor spool turns approximately 70°. In an opposed pair, one side takes up that amount while the other pays out the same amount; twice this quantity is the total differential cable-length change. These are idealized calculations; guide geometry, wrap and compliance must be calibrated physically.

Output shaft offsets, horn seating planes, bolt patterns and shaft/hub coupling remain provisional. The model uses a stock-horn adapter concept and never invents a printable replacement motor spline. Verify each interface against the chosen supplier CAD before fabrication. The motor models are dimensioned packaging envelopes, not supplier-certified replicas.

## Wrist and tendon routing

The fixed radiocarpal fork attaches to the two rails. A flexion axle drives the carpal gimbal through an external sector. The hand carrier rotates around a second axle on the moving gimbal. Its integrated sector drives radial/ulnar deviation. Axles need positive torque coupling where driven, bushings, thrust washers and retention hardware. The shaft coupling notes in the parts manifest identify what remains to detail.

Finger Bowden sheaths continue across the wrist in flexible service loops and terminate in a reaction anchor attached to the palm. Anchoring on the moving hand prevents ordinary wrist movement from simply pulling the fingers closed. The deviation sheaths likewise need moving-gimbal reaction endpoints. Sheaths cannot be replaced by a loose tube guide without changing this behavior.

The retinaculum-inspired distal bridge organizes the sheath bundle. Orange paths in the preview are schematic routing centerlines; they are not exact manufactured sheaths, force simulations or validated bend radii. Final paths need a minimum bend-radius check, positive ferrules, abrasion-resistant liners, pretension adjustment and sufficient slack through the entire wrist range. Include spring tension adjustment on both wrist antagonists so neither strand goes slack or overloads at the extremes.

## Fabrication and next engineering steps

Start with one finger, the wrist fork/gimbal/carrier, motor interface coupons and one motor cradle. Fit steel pins and bushings, then measure friction, return reliability and actual tendon take-up. PA12 SLS/MJF is a useful starting process for the structural parts; validate material strength and creep rather than treating a printed solid as a qualified structure. Use TPU or cast silicone contact pads. Retain all axles mechanically and keep fastener heads clear of sheath bends.

The paired rails use capped ends and axial M4 attachment bores. End nut access, washers and captive hardware require the final assembly detail. The shell is removable for access to the proximal cassette. Cover seam fasteners, motor clamps and parts that depend on a selected supplier should be reviewed before ordering prints.

A1 digital checks report solid validity, mesh closure and sampled exact-solid interference in `output/A1/geometry_report.json` and `output/A1/motion_report.json`. Zero intersections in sampled poses does not prove the whole workspace, tendon clearance or strength. Some combinations of finger curl and thumb opposition cause self-contact; a local controller must constrain such commands, and physical range stops still need detailing. Add guarded mechanical stops, tension sensing, wrist load testing and thermal tests before powered use.

The VLM remains secondary: camera and task text can be interpreted offboard using an appropriate Nemotron vision model, while a deterministic local controller handles eight motor channels, current/tension limits, rate limits, collision constraints and watchdog behavior. No VLM software or force-control implementation is claimed in this CAD package.
