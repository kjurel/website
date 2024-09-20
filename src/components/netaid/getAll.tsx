import { createSignal, createEffect } from 'solid-js';
import { client } from "@/utils/trpc";

const UserTableModal = () => {
  let modalRef!: HTMLDialogElement;
  const [users, setUsers] = createSignal<{ id: string; name: string; aadhar_no: string }[]>([]);
  const [isOpen, setIsOpen] = createSignal(false);
  const [markedForDeletion, setMarkedForDeletion] = createSignal<string[]>([]);
  const [adminPassword, setAdminPassword] = createSignal('');


  const fetchUsers = async () => {
    try {
      const userData = await client.netaid.getAllUsers.query(); // Adjust to your query method
      setUsers(userData);
    } catch (error) {
      console.error("Error fetching users:", error);
    }
  };

  const closeModal = () => {
    setIsOpen(false);
    modalRef.close();
  };

  const toggleMarkForDeletion = (userId: string) => {
    setMarkedForDeletion((prev) => {
      if (prev.includes(userId)) {
        return prev.filter((id) => id !== userId);
      } else {
        return [...prev, userId];
      }
    });
  };


  const deleteMarkedUsers = async () => {
    if (adminPassword() === "admin") {
      try {
        // await client.netaid.deleteUsers.mutate(markedForDeletion()); // Adjust to your delete method
        setMarkedForDeletion([]); // Clear the list after deletion
        closeModal();
        alert('Selected users deleted successfully!');
      } catch (error) {
        console.error("Error deleting users:", error);
        alert('Failed to delete users.');
      }
    } else {
      alert('Please enter the correct admin password.');
    }
  };




  return (
    <div>
      <button class="btn" onClick={async () => {
        await fetchUsers();
        setIsOpen(true);
        modalRef.showModal();
      }}>Show Users</button>

      <dialog ref={modalRef} class="modal">
        <div class="modal-box">
          <h3 class="text-lg font-bold">User List</h3>
          <table class="table w-full mt-4">
            <thead>
              <tr>
                <th>User ID</th>
                <th>Name</th>
                <th>Aadhar Number</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {users().map(user => (
                <tr key={user.id}>
                  <td>{user.id}</td>
                  <td>{user.name}</td>
                  <td>{user.aadhar_no}</td>
                  <td>
                    <button
                      class="btn btn-xs"
                      onClick={() => toggleMarkForDeletion(user.id)}>
                      {markedForDeletion().includes(user.id) ? 'o' : '-'}
                    </button>
                  </td>
                </tr>
              ))}

            </tbody>
          </table>
          <div class="modal-action">
            <button class="btn" onClick={closeModal}>Close</button>
          </div>
        </div>
      </dialog>
    </div>
  );
};

export default UserTableModal;

