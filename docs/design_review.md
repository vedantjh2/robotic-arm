# Tendon Hand A0 — design review

Design study for a final-year mechanical prototype, from proximal forearm mounting flange to fingertips. This package supplies actual solid CAD, STL parts, a Blender scene builder, and an inspectable preview. A0 is an engineering concept for review and iteration; it has not been physically built, load-tested, or qualified for manufacture.

## Architecture

- Right, approximately adult-size hand; four three-joint fingers and a thumb with two flexion joints plus one opposition pivot.
- Six independently commanded motor channels, all inside the forearm. M1 index, M2 middle, M3 ring, M4 little, M5 thumb flexion, M6 thumb opposition.
- One flexor tendon per finger. One motor curls the associated joints together; joint angles emerge from contact, elastic return stiffness, and friction. The model contains 15 moving joints and six actuation channels. It does not promise independent control of all 15 joints.
- Passive dorsal elastic return at each hinge, plus an opposition return. Tendons pull; opening occurs when the spool pays out and the elastic return extends the joints.
- Fixed wrist, proximal mounting flange, no powered elbow and no pronation/supination in this revision.
- Steel pinned joints with replaceable printed modules; thumb swivels about a separate M5 axle. No hand motors.

Tendon underactuation and passive adaptation are established approaches; see [Yale OpenHand](https://www.eng.yale.edu/grablab/openhand/). These CAD parts are an original concept, not a downloaded Yale hand or a validated reproduction.

## Nominal geometry

All CAD uses millimeters. +y is distal toward fingertips, +z is palmar, x runs across the palm. The arm lies flat in the CAD coordinate system; the proximal flange is the elbow-side attachment.

| Item | Nominal design |
|---|---|
| Palm frame | 90 × 82 × 8 mm, plus thumb ledge |
| Index / middle / ring / little link centers | 40–25–22 / 44–28–23 / 41–26–22 / 32–21–20 mm |
| Thumb links | 35–28 mm |
| Finger hinge pin | 3 mm steel; 3.3 mm printed bore |
| Fork gap / central lug | 9.0 / 8.2 mm, 0.4 mm per side |
| Flexor guides | 2.6 mm bore; nominal 7.5 mm lever arm |
| Forearm body | 106 mm wide, 240 mm long, 66 mm body height including floor |
| Proximal flange | 110 mm wide, 72 mm high; four 6.5 mm mounting bores |
| Tendon spool | 24 mm core diameter, 30 mm flange diameter, one working wrap |
| Candidate servo envelope | 28.5 × 46.5 × 34 mm |

The forearm chassis is approximately 110 × 248 × 72 mm including flange. The wrist bridge extends distal to it. Choose a printer with enough bed volume or split the chassis using keyed, bolted joints in the receiving CAD application.

## Tendon system

Use approximately 0.8 mm braided UHMWPE line as a starting selection, with 2 mm ID / 4 mm OD PTFE-lined sheaths for the forearm runs. Confirm line specifications, knot derating, creep, and abrasion with the supplier. The sheaths must be positively clamped at their ends; a loose guide is not a Bowden reaction anchor.

A0's orange preview routes show the intended motor-to-finger connection. They are schematic centerlines, not a manufactured pulley path. The printable combs support sheaths; the final compression ferrules and end clamps are purchased components to locate after selecting the tubing. Maintain generous bend radii, avoid adjacent spool flanges and clamp screws, and use replaceable polished liners at the finger guides. Do not tension cord directly over a sharp printed edge.

Thread each flexor from its spool through its own sheath, through each palmar phalanx guide, and loop it around the distal transverse anchor. Clamp the end mechanically, leaving enough adjustment for retensioning. Elastic returns pass through the dorsal transverse eyes across each hinge. Select their stiffness on a single-finger rig; use weaker proximal/stronger distal or other experimentally selected stiffness to tune the curling sequence. The preview pose is a kinematic illustration, not a prediction of underactuated behavior.

The spine rail on each fork supports the next segment at zero extension. Its clearance is included in the motion audit. Maximum flexion is initially bounded by control limits. Positive mechanical flexion and opposition stops still need detail design and validation after the collision sweep. A spring return can fail to open under sheath friction; verify release in all intended poses.

## Motors and sizing

ROBOTIS publishes the [XL430-W250-T envelope and electrical specification](https://emanual.robotis.com/docs/en/dxl/x/xl430-w250/): 28.5 × 46.5 × 34 mm, 57.2 g, 6.5–12 V, position / extended position / PWM modes. Published 1.5 N·m at 12 V is **stall torque**, not allowable continuous torque. A0 uses its body envelope for packaging only; this is not a final actuator procurement decision.

The motor center-of-output offset, horn seating plane, bolt circle, and pilot are explicitly provisional in `cad/parameters.json`. Use the selected supplier drawing to replace those values before printing motor interfaces. A strap-mounted body cradle avoids guessing threaded body holes. A matching stock output horn must bolt to the spool. Confirm that screw heads sit inside the flange and cannot catch the cord. The motor bodies in STEP/GLB are simplified envelopes, not supplier-certified motor CAD.

For first-order calculations: motor torque = tendon tension × spool radius; joint torque ≈ tendon tension × tendon moment arm. With a 12 mm spool and 25 N tendon design load, required ideal motor torque is 0.30 N·m. Applying a 1.5 factor gives 0.45 N·m. That is a sizing assumption requiring thermal/duty testing, not a verified XL430 continuous rating. At 25 N and 7.5 mm leverage, the ideal hinge moment is 0.1875 N·m; spring force and friction reduce the available contact moment. No payload rating can be inferred from this number alone.

Start commissioning at 8 N per tendon with a force gauge and external load sensing. The XL430's Present Load value is an inferred load indication; this motor has no true current-control mode or calibrated tendon force sensor. Do not call PWM or reported load a current/force controller. A force-sensitive series tensioner or load cell, and a motor with supported current limiting if needed, are design upgrades for repeatable force control.

Four-finger range assumption: 75° MCP + 90° PIP + 60° DIP. Constant 7.5 mm moment arms give approximately 29.45 mm take-up and 140.6° of 12 mm-radius spool rotation. Thumb flexion gives approximately 17.67 mm and 84.4°. A 90° opposition range at a 12 mm sector gives approximately 18.85 mm and 90° of spool rotation. These are idealized sizing calculations. Straight fairlead geometry does not give exactly constant moment arms; measure take-up through the actual path on the single-finger rig. Reserve about 20% additional stroke, keep a retaining wrap, and prevent layering that changes the effective spool radius.

## Manufacturing and assembly

1. First print `fit_coupon`, one `mcp_root`, and all three index links. Review pin fit, joint clearance, guide access, extension stop contact, and cord abrasion before committing to all parts.
2. Use PA12 (SLS/MJF) for joint modules and chassis where accessible; PETG is an iterative alternative. Use TPU or cast silicone contact pads. Material labels are suggestions, not structural certification.
3. Align layers and supports so the hinge ears do not split at their roots. Deburr and ream printed bores to fit steel pins. Preserve the 0.4 mm axial lug clearance; adjust the parameter to suit the print process.
4. Install retained M3 steel pins / shoulder bolts. The CAD depicts pin shanks; heads, locknuts, washers, and keepers are purchased hardware and are not fully modeled. Put retention hardware outside the tendon paths.
5. Bolt MCP root feet to the palm and install the thumb housing from beneath the palm. The housing sits in the clearance pocket. Use an M5 shoulder axle, polymer/bronze sleeve if required, washers, and a locknut; prevent tightening the nut onto the moving carrier.
6. Add low-preload elastic returns, lubricated guide inserts if compatible with the chosen line, and pads. Confirm manual joint motion before installing tendons.
7. Bolt palm to fixed wrist bridge and bridge to forearm floor. Seat each servo on a compliant shim, secure with two clamps, fit the horn/spool, and calibrate open spool angles with tendons detached.
8. Clamp sheath ends, connect and pretension tendons, then test one finger at a time. Check the full motion with temporary guards. Install the vented forearm cover after checking clearance.
9. Mount the proximal flange to a rigid bench fixture using four M6 fasteners. Fixture strength and center of mass require a separate check.

The slots and open palm are service features; they do not seal the mechanism. A removable palm skin, fingertip sensing, positively captive ferrules, tension adjustment, and mechanical range stops are next-detail items. This revision should be sent to a printing company as a **design review package**, with those interfaces called out, rather than an unconditional fabrication release.

## Electronics and VLM boundary

Keep motor power and inference compute separate. Use an externally powered 11.1–12 V motor bus (within the final actuator specification), branch protection, a hard power disconnect, and a controller with watchdog and rate/position limits. Six published 1.4 A stall currents total 8.4 A; this is a transient provisioning reference, not normal measured consumption. Final wire, connector, fuse, and supply sizing depend on chosen actuators and measured duty.

The user's NVIDIA reference is likely **Nemotron**. [Nemotron Nano 12B v2 VL](https://docs.api.nvidia.com/nim/reference/nvidia-nemotron-nano-12b-v2-vl) accepts text, images and video. Despite “Nano,” it contains roughly 12.6 billion parameters; do not assume it runs on a small microcontroller or fits a low-memory edge module. Initially use a workstation/API for VLM task interpretation. Leave physical space for a camera and control interface; host the model off the hand while the hardware is being developed.

Suggested future path: camera + task text → VLM → a small permitted grasp command (`open`, `power_grasp`, `pinch`, `release`) → deterministic local controller → six motor channels. The VLM does not directly issue PWM. Vision alone is not sufficient to infer tendon tension. This package deliberately does not claim implemented perception, closed-loop control, or VLM integration.

## Required next reviews

- Verify exact motor/horn interfaces and motor output offset against vendor CAD.
- Resolve sampled motion-audit collisions; supply real joint and opposition stops.
- Design positive sheath ferrules, tension adjustment, and cord termination retention.
- Confirm thumb opposition contact and wrist/palm load paths using full motion plus a physical finger test.
- Analyze/experimentally test pin shear, ear bearing stress, printed layer strength, clamp creep, and cable wear.
- Determine return stiffness, real tendon travel, force limit, temperature rise, and sustainable grasp duration.

Geometry-valid STEP/STL is evidence of a sound digital solid, not evidence of a functioning or load-rated robot.
