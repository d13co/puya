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

    @arc4.abimethod(allow_actions=["DeleteApplication"])
    def delete(self) -> None:
        pass

    @arc4.abimethod()
    def greet(self, name: String) -> String:
        return self.greeting + " " + name


class HelloFactory(ARC4Contract):

    @arc4.abimethod()
    def test_get_program(self) -> None:
        # create app
        hello_app = (
            itxn.ApplicationCall(
                app_args=(arc4.arc4_signature("create(string)void"), arc4.String("hello")),
                approval_program=get_approval_program(Hello),
                clear_state_program=get_clear_state_program(Hello),
                global_num_bytes=1,
            )
            .submit()
            .created_app
        )

        # call the new app
        txn = itxn.ApplicationCall(
            app_args=(arc4.arc4_signature("greet(string)string"), arc4.String("world")),
            app_id=hello_app,
        ).submit()
        result = arc4.String.from_log(txn.last_log)

        # delete the app
        itxn.ApplicationCall(
            app_id=hello_app,
            app_args=(arc4.arc4_signature("delete()void"),),
            on_completion=OnCompleteAction.DeleteApplication,
        ).submit()

        assert result == "hello world"

    @arc4.abimethod()
    def test_abi_call(self) -> None:
        # create app
        hello_app = arc4.abi_call(
            Hello.create,
            "hello",
            # approval_program, clear_state_program, global_num_*, local_num_*, and
            # extra_program_pages are automatically set based on Hello contract
        ).created_app

        # call the new app
        result, _txn = arc4.abi_call(Hello.greet, "world", app_id=hello_app)

        # delete the app
        arc4.abi_call(
            Hello.delete,
            app_id=hello_app,
            # on_complete is inferred from Hello.delete ARC4 definition
        )

        assert result == "hello world"
