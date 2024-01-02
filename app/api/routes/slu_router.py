import logging

from fastapi import APIRouter, Depends, HTTPException, status

from app.db.events import get_db
from app.error_handler import ChatbotException
from app.models.schemas.slu_schema import (
    CreateSkillRequest,
    DeployIndexRequest,
    DeployIndexResponse,
    DeployModelResponse,
    DeployModelResquest,
    ListSkill,
    ListSkillAll,
    QueryRequest,
    QueryResponse,
    TestModelRequest,
)
from app.services.chatbot_manager import CHATBOT_MANAGER
from app.services.manager.slu_manager import SluSkillManager
from app.services.skills.slu_skill import SluSkill

router = APIRouter()


@router.post(
    "/{chatbot_pk}/slus",
    response_model=ListSkill,
    status_code=status.HTTP_201_CREATED,
    tags=["SLU"],
    summary="創建skill",
)
def create_slu_skill(chatbot_pk: int, skill_data: CreateSkillRequest, _db: get_db = Depends()):
    chatbot_service = CHATBOT_MANAGER.get_service(chatbot_pk)
    if not chatbot_service:
        raise ChatbotException(chatbot_id=chatbot_pk, chatbot_exist=chatbot_service)
    skill_manager = None
    if "SLU" in chatbot_service.skill_manager:
        skill_manager = chatbot_service.get_manager("SLU")
    else:
        skill_manager = SluSkillManager(_db, chatbot_pk)
        chatbot_service.add_skill_manager(_db, "SLU", skill_manager)

    slu_data = skill_manager.create_skill(_db, skill_data)
    logging.info(f"create slu skill {slu_data.id} in chatbot {chatbot_pk}")
    return slu_data


@router.get(
    "/{chatbot_pk}/slus",
    response_model=ListSkillAll,
    status_code=status.HTTP_200_OK,
    tags=["SLU"],
    summary="條列所有skill",
)
def get_all_slu_skill(chatbot_pk: int, _db: get_db = Depends()):
    chatbot_service = CHATBOT_MANAGER.get_service(chatbot_pk)
    if not chatbot_service or "SLU" not in chatbot_service.skill_manager:
        raise ChatbotException(
            chatbot_id=chatbot_pk, chatbot_exist=chatbot_service, skill_name="SLU"
        )
    skill_manager = chatbot_service.get_manager("SLU")
    slu_list = skill_manager.get_all_skills(_db)
    return {"all_skill_info": slu_list}


@router.get(
    "/{chatbot_pk}/slus/{slu_id}",
    response_model=ListSkill,
    status_code=status.HTTP_200_OK,
    tags=["SLU"],
    summary="條列特定skill",
)
def get_certain_slu_skill(chatbot_pk: int, slu_id: int, _db: get_db = Depends()):
    chatbot_service = CHATBOT_MANAGER.get_service(chatbot_pk)
    if not chatbot_service or "SLU" not in chatbot_service.skill_manager:
        raise ChatbotException(
            chatbot_id=chatbot_pk, chatbot_exist=chatbot_service, skill_name="SLU"
        )
    skill_manager = chatbot_service.get_manager("SLU")
    slu_list = skill_manager.get_certain_skill(_db, slu_id)
    return slu_list


@router.delete(
    "/{chatbot_pk}/slus/{slu_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["SLU"],
    summary="刪除skill",
)
def delete_slu_skill(chatbot_pk: int, slu_id: int, _db: get_db = Depends()):
    chatbot_service = CHATBOT_MANAGER.get_service(chatbot_pk)
    if not chatbot_service or "SLU" not in chatbot_service.skill_manager:
        raise ChatbotException(
            chatbot_id=chatbot_pk, chatbot_exist=chatbot_service, skill_name="SLU"
        )
    skill_manager = chatbot_service.get_manager("SLU")
    skill_manager.delete_skill(_db, slu_id)
    logging.info(f"delete slu skill {slu_id} in chatbot {chatbot_pk}")
    if skill_manager.skill_services is None or not bool(skill_manager.skill_services):
        chatbot_service.delete_skill_manager(_db, "SLU")


@router.put(
    "/{chatbot_pk}/slus/{slu_id}/deploy",
    response_model=DeployModelResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["SLU"],
    summary="部署模型至skill",
)
def deploy_model_to_skill(
    chatbot_pk: int, slu_id: int, deploy_data: DeployModelResquest, _db: get_db = Depends()
):
    chatbot_service = CHATBOT_MANAGER.get_service(chatbot_pk)
    if (
        not chatbot_service
        or "SLU" not in chatbot_service.skill_manager
        or "ModelManager" not in chatbot_service.skill_manager
    ):
        raise ChatbotException(
            chatbot_id=chatbot_pk, chatbot_exist=chatbot_service, skill_name="SLU or ModelManager"
        )
    slu_manager = chatbot_service.get_manager("SLU")
    model_manager = chatbot_service.get_manager("ModelManager")
    target_model_data = model_manager.get_certain_model(_db, deploy_data.model)
    if target_model_data.skill_id != slu_id:
        logging.warning(
            f"Mismatched skill_id: Model {target_model_data.id} has a different skill_id than the current skill {slu_id}"
        )
    slu_data = slu_manager.deploy_model(_db, slu_id, target_model_data.id, target_model_data.task)
    logging.info(f"deploy model {target_model_data.id} to slu skill {slu_id}")
    return {"model": slu_data.model, "skill_id": slu_data.id, "task": slu_data.task}


@router.put(
    "/{chatbot_pk}/slus/{slu_id}/term_index",
    response_model=DeployIndexResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["SLU"],
    summary="部署專有名詞文件至skill",
)
def deploy_term_index_to_skill(
    chatbot_pk: int, slu_id: int, deploy_data: DeployIndexRequest, _db: get_db = Depends()
):
    chatbot_service = CHATBOT_MANAGER.get_service(chatbot_pk)
    if not chatbot_service or "SLU" not in chatbot_service.skill_manager:
        raise ChatbotException(
            chatbot_id=chatbot_pk, chatbot_exist=chatbot_service, skill_name="SLU"
        )
    skill_manager = chatbot_service.get_manager("SLU")
    slu_data = skill_manager.deploy_term_index(_db, slu_id, deploy_data.index_name)
    if not slu_data:
        logging.error(f"{deploy_data.index_name} does not exist")
        raise HTTPException(status_code=500, detail=f"{deploy_data.index_name} does not exist")
    logging.info(f"deploy term_index {deploy_data.index_name} to slu skill {slu_id}")
    return {"name": slu_data.name, "skill_id": slu_data.id, "term_index": slu_data.term_index}


@router.post(
    "/{chatbot_pk}/slus/{slu_id}/query",
    response_model=QueryResponse,
    status_code=status.HTTP_200_OK,
    tags=["SLU"],
    summary="SLU推論",
)
def query(chatbot_pk: int, slu_id, query_data: QueryRequest, _db: get_db = Depends()):
    chatbot_service = CHATBOT_MANAGER.get_service(chatbot_pk)
    if (
        not chatbot_service
        or "SLU" not in chatbot_service.skill_manager
        or "ModelManager" not in chatbot_service.skill_manager
    ):
        raise ChatbotException(
            chatbot_id=chatbot_pk, chatbot_exist=chatbot_service, skill_name="SLU or ModelManager"
        )
    slu_manager = chatbot_service.get_manager("SLU")
    model_manager = chatbot_service.get_manager("ModelManager")
    skill_data = slu_manager.get_certain_skill(_db, slu_id)
    target_model_data = model_manager.get_certain_model(_db, skill_data.model)
    model_obj = model_manager.get_skill(target_model_data.id)
    slu_obj = slu_manager.get_skill(skill_data.id)
    model_path = model_obj.get_model_from_mlflow(target_model_data.id)
    logging.info(
        f"Question: '{query_data.ques}' Model:{target_model_data.id} Task:'{skill_data.task}' Correction:'{query_data.use_correction}' Term_index:'{skill_data.term_index}'"
    )

    sentence, intent, slot, correction = slu_obj.inference(
        query_data.ques, model_path, query_data.use_correction
    )
    response = {"ques": sentence, "intent": intent, "slot": slot, "correction_result": correction}
    if skill_data.task == "SLU-intent":
        response.pop("slot")
    elif skill_data.task == "SLU-slot":
        response.pop("intent")
    else:
        return response
    return response


@router.post(
    "/{chatbot_pk}/slus/test",
    response_model=QueryResponse,
    status_code=status.HTTP_200_OK,
    tags=["SLU"],
    summary="測試模型效果",
)
def test_model(chatbot_pk: int, test_data: TestModelRequest, _db: get_db = Depends()):
    chatbot_service = CHATBOT_MANAGER.get_service(chatbot_pk)
    if not chatbot_service or "ModelManager" not in chatbot_service.skill_manager:
        raise ChatbotException(
            chatbot_id=chatbot_pk, chatbot_exist=chatbot_service, skill_name="ModelManager"
        )
    model_manager = chatbot_service.get_manager("ModelManager")
    model_data = model_manager.get_certain_model(_db, test_data.model)
    model_obj = model_manager.get_skill(model_data.id)
    model_path = model_obj.get_model_from_mlflow(model_data.id)
    slu_obj = SluSkill(None, model_data.task, model_data.id, test_data.term_index)
    logging.info(
        f"Question: '{test_data.ques}' Model:{model_data.id} Task:'{model_data.task}' Correction:'{test_data.use_correction}' Term_index:'{test_data.term_index}'"
    )
    sentence, intent, slot, correction = slu_obj.inference(
        test_data.ques, model_path, test_data.use_correction
    )

    response = {"ques": sentence, "intent": intent, "slot": slot, "correction_result": correction}
    if model_data.task == "SLU-intent":
        response.pop("slot")
    elif model_data.task == "SLU-slot":
        response.pop("intent")
    else:
        return response
    return response
