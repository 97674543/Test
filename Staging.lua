local assets =
{
    Asset("ANIM", "anim/sample_projectile.zip"),
}

local function OnHit(inst, owner, target)
    inst.SoundEmitter:PlaySound("hinozuki/hinozuki/blast")
    inst:Remove()
end

local function common(anim, bloom)
    local inst = CreateEntity()

    inst.entity:AddTransform()
    inst.entity:AddAnimState()
	inst.entity:AddSoundEmitter()
    inst.entity:AddNetwork()

    MakeInventoryPhysics(inst)
    RemovePhysicsColliders(inst)
		
	inst.Transform:SetScale(1, 1, 1)

    inst.AnimState:SetBank("sample_projectile")
    inst.AnimState:SetBuild("sample_projectile")
    inst.AnimState:PushAnimation("idle", true)
	
    inst:AddTag("projectile")

    if not TheWorld.ismastersim then
        return inst
    end

    inst.entity:SetPristine()
	
	inst.persists = false
    
    inst:AddComponent("projectile")
    inst.components.projectile:SetSpeed(50)
    inst.components.projectile:SetOnMissFn(inst.Remove)
	inst.components.projectile:SetOnHitFn(OnHit)

    return inst
end

local function sample_projectile()
    return common("idle")
end


return Prefab("common/inventory/sample_projectile", sample_projectile, assets)
