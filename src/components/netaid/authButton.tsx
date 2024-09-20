import { createSignal } from 'solid-js';
import { client } from "@/utils/trpc";
import { z } from 'zod';

const AuthModal = () => {
  let modalButton!: HTMLButtonElement;
  let modalDialog!: HTMLDialogElement;

  const [isLogin, setIsLogin] = createSignal(true);
  const [formData, setFormData] = createSignal({ name: '', password: '', aadhar_no: '' });
  const [user, setUser] = createSignal<{ name: string } | null>(null);


  const handleInputChange = (e: Event) => {
    const target = e.target as HTMLInputElement;
    setFormData({ ...formData(), [target.name]: target.value });
  };

  const handleSubmit = async (e: Event) => {
    e.preventDefault();
    const data = formData();

    try {
      if (isLogin()) {
        const login_res = await client.netaid.login.mutate({
          username: data.name,
          password: data.password,
        });
        if (login_res) alert('Login successful!');
        else alert('Login unsuccessful')
      } else {
        const register_res = await client.netaid.register.mutate({
          name: data.name,
          password: data.password,
          aadhar_no: Number(data.aadhar_no),
        });
        if (register_res) alert('Registration successful!');
        else alert('Registration unsuccessful')
      }
    } catch (error: any) {
      alert(error.message || 'An error occurred');
    }
  };

  return (
    <>
      <button ref={modalButton} class="btn" onclick={() => {
        setFormData({ name: '', password: '', aadhar_no: '' });
        modalDialog.showModal()
      }} disabled={!!user()}>
        {user() ? `Logged in as ${user()!.name}` : 'Login/Register'}
      </button>
      <dialog ref={modalDialog} class="modal modal-bottom sm:modal-middle">
        <div class="modal-box">
          <form onSubmit={handleSubmit} class="p-4 bg-base-200 rounded-lg shadow-md">
            <h3 class="text-lg font-bold">{isLogin() ? 'Login' : 'Register'}</h3>
            <div class="form-control mb-4">
              <label class="label">
                <span class="label-text">Name</span>
              </label>

              <input
                type="text"
                name="name"
                placeholder="Name"
                value={formData().name}
                onInput={handleInputChange}
                required
                class="input input-bordered"
              />
            </div>
            <div class="form-control mb-4">
              <label class="label">
                <span class="label-text">Password</span>
              </label>

              <input
                type="password"
                name="password"
                placeholder="Password"
                value={formData().password}
                onInput={handleInputChange}
                required
                class="input input-bordered"
              />
            </div>
            {!isLogin() && (
              <div class="form-control mb-4">
                <label class="label">
                  <span class="label-text">Aadhar Number</span>
                </label>

                <input
                  type="text"
                  name="aadhar_no"
                  placeholder="Aadhar Number"
                  value={formData().aadhar_no}
                  onInput={handleInputChange}
                  required
                  class="input input-bordered"
                />
              </div>
            )}
            <button type="submit" class="btn btn-primary w-full mt-4">{isLogin() ? 'Login' : 'Register'}</button>
          </form>
          <button onClick={() => setIsLogin(!isLogin())} class="btn btn-link mt-2 w-full">
            Switch to {isLogin() ? 'Register' : 'Login'}
          </button>
        </div>
        <form method="dialog" class="modal-backdrop">
          <button>Close</button>
        </form>
      </dialog >
    </>
  );
};

export default AuthModal;

