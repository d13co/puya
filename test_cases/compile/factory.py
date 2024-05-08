from algopy import (
    ARC4Contract,
    OnCompleteAction,
    String,
    arc4,
    get_approval_program,
    get_clear_state_program,
    itxn,
)


class Hello(ARC4Contract):

    @arc4.abimethod(create="require")
    def create(self, greeting: String) -> None:
        self.greeting = greeting

    @arc4.baremethod(allow_actions=["DeleteApplication"])
    def delete(self) -> None:
        pass

    @arc4.abimethod()
    def greet(self, name: String) -> String:
        return self.greeting + " " + name


class HelloFactory(ARC4Contract):

    @arc4.abimethod()
    def do_some_stuff(self) -> None:
        # create app
        hello_app = arc4.abi_call(
            Hello.create,
            "hello",
            approval_program=get_approval_program(Hello),
            clear_state_program=get_clear_state_program(Hello),
            global_num_bytes=1,
        ).created_app

        # call the new app
        result, _txn = arc4.abi_call(Hello.greet, "world", app_id=hello_app)

        # delete the app
        itxn.ApplicationCall(
            app_id=hello_app,
            on_completion=OnCompleteAction.DeleteApplication,
        ).submit()

        assert result == "hello world"
