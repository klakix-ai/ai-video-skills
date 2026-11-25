# Camera library: tested prompt wording

Each entry was used in real productions on Seedance 2.x, Kling and MiniMax. Copy the
wording, then adapt subject and lens. Keep one move per shot.

## 1. Snap zoom + hold (over-the-shoulder, foreground blur)

When: the reveal or punchline. 0 to 2 s static, one fast zoom-in, then a sharp hold. Cut
it on the beat or the music drop. Our audience's favourite move.

```
Over-the-shoulder medium shot from just behind the character's shoulder on a 50mm lens:
her collar and hair softly out of focus in the foreground, the subject sharp in its niche.
0-2s: the camera is still. At 2s a fast snap zoom-in to the key detail, then hold steady
and sharp. No whip pans, no shake, no motion blur.
```

## 2. Locked-off low hero angle

When: opening hook, ground-level hero moments. The lens sits just above the ground; the
camera never moves.

```
Heroic low-angle shot with the lens just above the ground, 24mm, looking up at the subject
against the sky; the camera is locked off and does not move; only the subject moves.
```

## 3. Static top-down drone

When: action that reads like a map (drifts, turns, crowds, formations). The camera is fully
static; the subject carries all the motion.

```
Static top-down overhead shot from a high drone, looking straight down; the camera does not
move at all; only the vehicles and the smoke move.
```

## 4. Slow motion + low-angle slow push-in

When: one visual "flex" moment (falling money, sparks, dust, water).

```
Slow motion, low angle on a 35mm lens, one very slow steady push-in toward the subject;
the falling objects hang in the air; nothing fast.
```

## 5. Symmetrical one-point perspective + slow dolly

When: banquets, ceremonies, throne rooms, any "authority" frame.

```
Perfectly symmetrical one-point-perspective shot down the length of the table, 28mm;
one slow, steady dolly push-in; no zoom, nothing fast.
```

## 6. Selfie POV

When: the character poses or talks to the viewer. Say "no phone visible" or the model
draws a second phone.

```
Selfie POV on a phone's 24mm lens at arm's length, eye level, no phone visible; steady with
tiny natural hand movement. At 2.5s a quick snap zoom-in, then hold steady and sharp.
```

## 7. Static over-the-shoulder on a screen or object

When: jokes that live on a phone, tablet or screen; car interiors. Pairs with the
`phone-screen-compositing` skill.

```
Camera static, over-the-shoulder close-up on a 50mm lens: the foreground shoulder softly out
of focus, the screen or object sharp; no movement.
```

## 8. FPV dive + follow (one continuous shot)

When: a single flight through a scene, transformations. Works best with a reference video
(3D blockout) that the model copies; see `3d-previs-to-ai-video`.

```
One continuous FPV drone shot, no cuts: dive onto the subject, fly through it and out,
circle it low and smooth. Copy every camera move of the reference video exactly; the camera
never loses the subject.
```

## 9. Rising aerial reveal

When: openings and scale. Measures around 1.1 px/frame, right at the limit: check it.

```
Top-down high aerial looking straight down, the camera slowly rising; thousands of figures
spread across the landscape in a formation.
```

## 10. Gimbal tracking

When: a walking or galloping subject. Held up even in 30-second single takes.

```
Smooth gimbal tracking shot following the subject at the same speed (walking pace or
gallop), steady and calm; no fast moves, no whip pans.
```

## 11. Slow handheld push-in (documentary)

When: dialogue and comedy that should feel observed, not staged.

```
Real handheld footage at eye level, medium-wide, almost still, with one very slow steady
push-in at walking pace; nothing fast.
```

## 12. Slow lateral dolly

When: along a line of people or riders, two-shots.

```
Smooth slow lateral dolly along the line at eye level, parallel to the subjects; the camera
moves steadily sideways, nothing else moves fast.
```

## 13. Locked tripod, wide or medium

When: the gag lives in the frame, not in the move. The most reliable instruction for
MiniMax/Hailuo. Add background life or it looks dead.

```
Locked-off camera on a tripod, completely static medium-wide shot, no zoom, no pan, single
continuous shot, no cuts.
```

## 14. In-car camera that faces the driver

When: FPV or 3D flights that enter a vehicle. Without this the driver disappears.

```
Inside the car the camera always stays in front of the seat backs facing the driver; he
never disappears from frame.
```

## Avoid

### A. Fast camera, speed ramps on generated footage

Never speed up a generated clip in the edit, and never stack several moves in one 8-second
shot. Measured: complaints at 2 to 5 px/frame, approval at 0.2 to 1.2.

```
Avoid: fast camera, speed ramps on generated footage, more than one camera move per shot.
Instead: one slow steady move, the subject carries the action.
```

### B. Whip pans, shake, motion blur

Never in the prompt. If you need speed, add a short glitch or white flash on the beat in
the edit, at 3 to 4 places in the whole video.

```
Always append: No whip pans, no shake, no motion blur, nothing fast.
```

### C. "Cinematic" colour and film words

"Film grain, cinematic grade, golden hour, lens flare, anamorphic" push the model toward a
CGI look and were called "suffocating" when stacked in post. See `ai-video-realism`.

```
Real documentary footage shot on location, natural true-to-life colours, real skin texture,
no CGI look, no colour grading, no film grain, no text on screen.
```

## Angle variety cheat sheet

Strong viral pieces never repeat an angle twice in a row. Rotate through:
ground level rushing at the lens · frame within a frame (seen through a tent gap or door) ·
over-the-shoulder from inside a vehicle · extreme close-up of an ordinary action ·
first-person and screen insert · night top-down/aerial · following from behind · low hero.
