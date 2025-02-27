class RedeemOctoplusPointsResponse:
  is_successful: bool
  errors: list[str]

  def __init__(
    self,
    is_successful: bool,
    errors: list[str]
  ):
    self.is_successful = is_successful
    self.errors = errors

class ClaimOctoplusRewardResponse:
  reward_id: str
  errors: list[str]

  def error(errors: list[str]):
    this = ClaimOctoplusRewardResponse()
    this.reward_id = None
    this.errors = errors

  def success(reward_id: str):
    this = ClaimOctoplusRewardResponse()
    this.reward_id = None
    this.errors = []
