import { world, system } from "@minecraft/server";

const SPACE_HEIGHT = 320;
const OXYGEN_MAX = 200; // 10 seconds of oxygen

world.afterEvents.playerSpawn.subscribe((event) => {
    const player = event.player;
    if (player.getDynamicProperty("oxygen") === undefined) {
        player.setDynamicProperty("oxygen", OXYGEN_MAX);
    }
});

system.runInterval(() => {
    for (const player of world.getAllPlayers()) {
        const pos = player.location;
        const dimension = player.dimension;
        const isPlayerInSpace = pos.y > SPACE_HEIGHT || dimension.id === "minecraft:the_end";

        // Handle Oxygen (every 5 ticks, effectively)
        let oxygen = player.getDynamicProperty("oxygen") ?? OXYGEN_MAX;
        const hasSpaceSuit = checkSpaceSuit(player);

        if (isPlayerInSpace && !hasSpaceSuit) {
            oxygen -= 5;
            if (oxygen <= 0) {
                player.applyDamage(2, { cause: "suffocation" });
                oxygen = 0;
            }
            player.onScreenDisplay.setActionBar(`§cOxygen: ${Math.ceil(oxygen / 20)}s§r`);
        } else {
            if (oxygen < OXYGEN_MAX) {
                oxygen += 10;
                if (oxygen > OXYGEN_MAX) oxygen = OXYGEN_MAX;
            }
        }
        player.setDynamicProperty("oxygen", oxygen);

        // Low Gravity Effect
        if (isPlayerInSpace) {
            player.addEffect("jump_boost", 10, { amplifier: 2, showParticles: false });
            player.addEffect("slow_falling", 10, { amplifier: 0, showParticles: false });
        }
    }
}, 5);

// Rocket logic runs more frequently for smoothness, but we only check riding players
system.runInterval(() => {
    const rockets = world.getDimension("minecraft:overworld").getEntities({ type: "space:rocket" });
    const moonRockets = world.getDimension("minecraft:the_end").getEntities({ type: "space:rocket" });

    [...rockets, ...moonRockets].forEach(rocket => {
        const rideable = rocket.getComponent("minecraft:rideable");
        const riders = rideable?.getRiders();

        if (riders && riders.length > 0) {
            const rider = riders[0];
            // Rocket goes up
            rocket.applyImpulse({ x: 0, y: 0.1, z: 0 }); // Reduced impulse for smoother flight

            if (rocket.dimension.id === "minecraft:overworld" && rocket.location.y > SPACE_HEIGHT + 20) {
                rider.teleport({ x: 0, y: 100, z: 0 }, { dimension: world.getDimension("minecraft:the_end") });
                rocket.remove();
                rider.sendMessage("§bWelcome to the Moon!§r");
            } else if (rocket.dimension.id === "minecraft:the_end" && rocket.location.y > 150) {
                rider.teleport({ x: 0, y: 330, z: 0 }, { dimension: world.getDimension("minecraft:overworld") });
                rocket.remove();
                rider.sendMessage("§aReturning to Earth...§r");
            }
        }
    });
}, 2);

function checkSpaceSuit(player) {
    const equipment = player.getComponent("minecraft:equippable");
    if (!equipment) return false;

    const head = equipment.getEquipment("head");
    const chest = equipment.getEquipment("chest");
    const legs = equipment.getEquipment("legs");
    const feet = equipment.getEquipment("feet");

    return head?.typeId === "space:space_helmet" &&
           chest?.typeId === "space:space_chestplate" &&
           legs?.typeId === "space:space_leggings" &&
           feet?.typeId === "space:space_boots";
}
